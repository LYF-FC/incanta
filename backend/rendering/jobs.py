"""Durable, conversation-owned rendering and restart reconciliation."""
from contextlib import contextmanager
from threading import Event, Lock, Thread
from time import monotonic, sleep, time
from uuid import uuid4

from backend.conversation_store import identifier, now, revision, text
from backend.errors import AppError
from backend.rendering.assets import Assets
from backend.rendering.comfyui_adapter import BARRIER, ComfyUI
from backend.rendering.workflow import Workflow

ACTIVE = "('submitting','running','cancel_requested','uncertain')"
TERMINAL = {'succeeded', 'failed', 'cancelled'}
PUBLIC_JOB = """
 SELECT j.*, a.id AS asset_id FROM render_jobs j LEFT JOIN visual_assets a
 ON a.job_id=j.id AND a.conversation_id=j.conversation_id AND a.rejected=0
"""


class RenderJobs:
    def __init__(self, store, settings, resources, inference, renderer=None, clock=time):
        self.store = store
        self.settings = settings
        self.resources = resources
        self.inference = inference
        self.assets = Assets(settings.render_output_root)
        self.clock = clock
        self._lock = Lock()
        self._wake = Event()
        self._closing = Event()
        self.chat_pending = Event()
        self._worker = None
        self.renderer = renderer
        self.setup_error = None
        if renderer is None and settings.renderer_url:
            try:
                self.renderer = ComfyUI(settings.renderer_url, settings.renderer_dedicated)
            except AppError as error:
                self.setup_error = error.code
        if settings.visuals_parse_failed:
            self.setup_error = 'renderer_incompatible'

    def _configured(self):
        if self.setup_error:
            raise AppError(self.setup_error)
        if self.renderer is None or self.settings.workflow_root is None or self.settings.render_output_root is None:
            raise AppError('renderer_unconfigured')

    def _workflow(self, selection):
        return Workflow.load(self.settings.workflow_root, self.settings.reference_root, selection)

    def status(self, selection=None):
        available = False
        dirty = self._handoff_row() is not None
        try:
            self._configured()
            self.renderer.inspect_capabilities()
            available = True
            self.assets.ready()
            if selection:
                self.renderer.validate_workflow(self._workflow(selection))
        except AppError as error:
            return {'configured': error.code != 'renderer_unconfigured',
                    'available': available, 'compatible': False, 'error': error.code, 'handoff_pending': dirty}
        return {'configured': True, 'available': True, 'compatible': bool(selection), 'error': None,
                'handoff_pending': dirty}

    @staticmethod
    def _identity(db, cid):
        row = db.execute('SELECT * FROM visual_identities WHERE conversation_id=?', (cid,)).fetchone()
        return dict(row) if row else {'revision': 1, 'configuration': None, 'approved_portrait_asset': None}

    @staticmethod
    def _policy(db, cid):
        row = db.execute('SELECT * FROM scene_policies WHERE conversation_id=?', (cid,)).fetchone()
        return {'revision': row['revision'], 'enabled': bool(row['enabled']),
                'cooldown_seconds': row['cooldown_seconds']} if row else {
                    'revision': 1, 'enabled': False, 'cooldown_seconds': 300}

    def set_identity(self, cid, body):
        expected = revision(body.get('revision'))
        if 'configuration' not in body:
            raise AppError('invalid_request')
        selection = body['configuration']
        compatible = False
        if selection is not None:
            workflow = self._workflow(selection)
            try:
                self._configured()
                self.renderer.validate_workflow(workflow)
                self.assets.ready()
                compatible = True
            except AppError as error:
                if error.code not in {'renderer_unavailable', 'renderer_unconfigured', 'asset_unavailable'}:
                    raise
        with self.store.connection(write=True) as db:
            self.store.row(db, cid)
            current = self._identity(db, cid)
            if expected != current['revision']:
                raise AppError('revision_conflict')
            db.execute('''INSERT INTO visual_identities(conversation_id,revision,configuration)
                          VALUES (?,?,?) ON CONFLICT(conversation_id) DO UPDATE
                          SET revision=excluded.revision, configuration=excluded.configuration''',
                       (cid, expected + 1, selection))
            self._stale_queued(db, cid)
            result = self._identity(db, cid)
        self._wake.set()
        return dict(result, compatible=compatible)

    def _stale_queued(self, db, cid):
        db.execute("""UPDATE render_jobs SET state='cancelled',error='render_stale',updated_at=?
                      WHERE conversation_id=? AND state='queued'""", (now(), cid))

    @staticmethod
    def _public(row):
        return {key: row[key] for key in ('id', 'request_id', 'kind', 'description',
                                           'state', 'asset_id', 'error', 'created_at', 'updated_at')}

    @staticmethod
    def _job(db, jid):
        row = db.execute(PUBLIC_JOB + ' WHERE j.id=?', (identifier(jid),)).fetchone() if db else None
        if row is None:
            raise AppError('not_found')
        return row

    def get(self, jid):
        with self.store.connection() as db:
            return self._public(self._job(db, jid))

    def list(self, cid, cursor=None, limit=50):
        if not 1 <= limit <= 100 or (cursor is not None and not 1 <= cursor < 2**63):
            raise AppError('invalid_request')
        with self.store.connection() as db:
            self.store.row(db, cid)
            rows = db.execute(PUBLIC_JOB + ''' WHERE j.conversation_id=? AND j.sequence<?
                                              ORDER BY j.sequence DESC LIMIT ?''',
                              (cid, cursor or 2**63 - 1, limit + 1)).fetchall()
            return {'identity': self._identity(db, cid), 'policy': self._policy(db, cid),
                    'jobs': [self._public(row) for row in rows[:limit]],
                    'next_cursor': rows[limit - 1]['sequence'] if len(rows) > limit else None}

    def _fresh(self, db, job):
        current = db.execute('SELECT settings_revision,context_revision FROM conversations WHERE id=?',
                             (job['conversation_id'],)).fetchone()
        identity = self._identity(db, job['conversation_id'])
        return (current is not None and tuple(current) == (job['settings_revision'], job['context_revision'])
                and identity['revision'] == job['identity_revision'])

    def _insert(self, db, current, identity, workflow, request_id, kind, description, turn_id=None):
        counts = db.execute("""SELECT count(*), count(CASE WHEN kind!='automatic' THEN 1 END)
                               FROM render_jobs WHERE state='queued'""").fetchone()
        if counts[0] >= 10 or (kind != 'automatic' and counts[1] >= 5):
            raise AppError('render_queue_full')
        jid, stamp = str(uuid4()), now()
        db.execute('''INSERT INTO render_jobs
                      (id,conversation_id,request_id,kind,description,settings_revision,context_revision,
                       identity_revision,workflow_digest,output_node,renderer_key,originating_turn,state,
                       created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,'queued',?,?)''',
                   (jid, current['id'], request_id, kind, description, current['settings_revision'],
                    current['context_revision'], identity['revision'], workflow.digest, workflow.output_node,
                    self.renderer.key, turn_id, stamp, stamp))
        return self._job(db, jid)

    def enqueue(self, cid, body):
        request_id = identifier(body.get('request_id'))
        description = text(body.get('description'), 1, 2000)
        kind = body.get('kind')
        if kind not in ('portrait', 'manual'):
            raise AppError('invalid_request')
        with self.store.connection(write=True) as db:
            current = self.store.row(db, cid)
            previous = db.execute(PUBLIC_JOB + ' WHERE j.conversation_id=? AND j.request_id=?',
                                  (cid, request_id)).fetchone()
            if previous:
                if (previous['kind'], previous['description']) != (kind, description):
                    raise AppError('request_conflict')
                return self._public(previous)
            self._configured()
            identity = self._identity(db, cid)
            workflow = self._workflow(identity['configuration'])
            result = self._public(self._insert(db, current, identity, workflow, request_id, kind, description))
        self._wake.set()
        return result

    @staticmethod
    def _transition(db, jid, state, error=None):
        db.execute('UPDATE render_jobs SET state=?,error=?,updated_at=? WHERE id=?',
                   (state, error, now(), jid))

    def cancel(self, jid):
        with self.store.connection(write=True) as db:
            job = self._job(db, jid)
            if job['state'] == 'queued':
                self._transition(db, jid, 'cancelled')
            elif job['state'] not in TERMINAL:
                db.execute("UPDATE render_jobs SET discard_reason='owner',updated_at=? WHERE id=?", (now(), jid))
                if job['state'] not in {'uncertain', 'submitting'}:
                    self._transition(db, jid, 'cancel_requested')
            result = self._public(self._job(db, jid))
            result['running_interrupt_supported'] = False
        self._wake.set()
        return result

    def resolve(self, jid):
        """Explicitly abandon a missing submission after the dedicated renderer is checked."""
        with self.resources.acquire('manual', jid, blocking=False) as acquired:
            if not acquired:
                raise AppError('conversation_busy')
            with self.store.connection() as db:
                job = self._job(db, jid)
            if job['state'] != 'uncertain':
                raise AppError('revision_conflict')
            self._matching_renderer(job)
            if not self.renderer.idle() or self.renderer.locate(jid):
                raise AppError('render_uncertain')
            with self.store.connection(write=True) as db:
                if self._job(db, jid)['state'] != 'uncertain':
                    raise AppError('revision_conflict')
                self._transition(db, jid, 'cancelled')
                result = self._public(self._job(db, jid))
        self._wake.set()
        return result

    def portrait(self, cid, body):
        asset_id = identifier(body.get('asset_id'))
        decision = body.get('decision', 'approve')
        if decision not in ('approve', 'reject'):
            raise AppError('invalid_request')
        with self.store.connection(write=True) as db:
            self.store.row(db, cid)
            row = db.execute(PUBLIC_JOB + """ WHERE a.id=? AND j.conversation_id=? AND j.kind='portrait'
                                            AND j.state='succeeded'""", (asset_id, cid)).fetchone()
            if row is None:
                raise AppError('not_found')
            if decision == 'approve':
                if not self._fresh(db, row):
                    raise AppError('render_stale')
                asset = db.execute('SELECT * FROM visual_assets WHERE id=?', (asset_id,)).fetchone()
                self.assets.read(asset)
                db.execute('UPDATE visual_identities SET approved_portrait_asset=? WHERE conversation_id=?',
                           (asset_id, cid))
            else:
                db.execute('UPDATE visual_assets SET rejected=1 WHERE id=?', (asset_id,))
                db.execute('''UPDATE visual_identities SET approved_portrait_asset=NULL
                              WHERE conversation_id=? AND approved_portrait_asset=?''', (cid, asset_id))
            return self._identity(db, cid)

    def asset(self, aid):
        identifier(aid)
        with self.store.connection() as db:
            row = db.execute('SELECT * FROM visual_assets WHERE id=? AND rejected=0', (aid,)).fetchone() if db else None
            if row is None:
                raise AppError('not_found')
            return self.assets.read(row)

    def set_policy(self, cid, body):
        expected = revision(body.get('revision'))
        enabled = body.get('enabled')
        cooldown = body.get('cooldown_seconds')
        if type(enabled) is not bool or type(cooldown) is not int or not 60 <= cooldown <= 3600:
            raise AppError('invalid_request')
        with self.store.connection(write=True) as db:
            self.store.row(db, cid)
            if self._policy(db, cid)['revision'] != expected:
                raise AppError('revision_conflict')
            db.execute('''INSERT INTO scene_policies(conversation_id,revision,enabled,cooldown_seconds)
                          VALUES (?,?,?,?) ON CONFLICT(conversation_id) DO UPDATE SET
                          revision=excluded.revision,enabled=excluded.enabled,cooldown_seconds=excluded.cooldown_seconds''',
                       (cid, expected + 1, enabled, cooldown))
            if not enabled:
                db.execute("""UPDATE render_jobs SET state='cancelled',updated_at=?
                              WHERE conversation_id=? AND kind='automatic' AND state='queued'""", (now(), cid))
            return self._policy(db, cid)

    def enabled_policy_revision(self, db, cid):
        policy = self._policy(db, cid)
        if self.renderer is not None and policy['enabled']:
            return policy['revision']
        return None

    def propose(self, cid, turn_id, description, policy_revision):
        """Only a committed turn from the same conversation may propose a scene."""
        try:
            self._configured()
            with self.store.connection(write=True) as db:
                policy = db.execute('SELECT * FROM scene_policies WHERE conversation_id=?', (cid,)).fetchone()
                if not policy or not policy['enabled'] or policy['revision'] != policy_revision:
                    return
                current = self.store.row(db, cid)
                turn = db.execute('SELECT * FROM turns WHERE conversation_id=? AND id=?', (cid, turn_id)).fetchone()
                if (turn is None or (turn['settings_revision'], turn['context_revision']) !=
                        (current['settings_revision'], current['context_revision'])):
                    return
                identity = self._identity(db, cid)
                workflow = self._workflow(identity['configuration'])
                pending = db.execute("""SELECT * FROM render_jobs WHERE conversation_id=?
                                        AND kind='automatic' AND state='queued'""", (cid,)).fetchone()
                if pending and self._fresh(db, pending) and pending['workflow_digest'] == workflow.digest:
                    if pending['description'] == description:
                        return
                    db.execute('UPDATE render_jobs SET description=?,originating_turn=?,updated_at=? WHERE id=?',
                               (description, turn_id, now(), pending['id']))
                else:
                    if pending:
                        self._transition(db, pending['id'], 'cancelled', 'render_stale')
                    clock = self.clock()
                    previous = policy['last_enqueue']
                    if previous is not None and clock - previous < policy['cooldown_seconds']:
                        return
                    latest = db.execute('''SELECT description FROM render_jobs WHERE conversation_id=?
                                            AND kind='automatic' AND state!='cancelled'
                                            ORDER BY sequence DESC LIMIT 1''', (cid,)).fetchone()
                    if latest and latest['description'] == description:
                        return
                    self._insert(db, current, identity, workflow, turn_id, 'automatic', description, turn_id)
                    db.execute('UPDATE scene_policies SET last_enqueue=? WHERE conversation_id=?', (clock, cid))
        except AppError:
            # An optional proposal must never alter a committed chat response.
            return
        self._wake.set()

    def _select(self, active=True):
        clause = f"WHERE state IN {ACTIVE}" if active else "WHERE state='queued'"
        with self.store.connection() as db:
            return db.execute(f"""SELECT * FROM render_jobs {clause}
                                  ORDER BY (kind='automatic'),sequence LIMIT 1""").fetchone() if db else None

    def _matching_renderer(self, row):
        self._configured()
        if row['renderer_key'] != self.renderer.key:
            raise AppError('renderer_incompatible')

    def _begin(self, jid):
        new_handoff = False
        try:
            with self.store.connection() as db:
                job = self._job(db, jid)
                if job['state'] != 'queued':
                    return
                if not self._fresh(db, job):
                    raise AppError('render_stale')
                selection = self._identity(db, job['conversation_id'])['configuration']
            self._matching_renderer(job)
            workflow = self._workflow(selection)
            if workflow.digest != job['workflow_digest']:
                raise AppError('render_stale')
            self.assets.ready()
            self.renderer.validate_workflow(workflow)
            if not self.renderer.idle():
                raise AppError('renderer_incompatible')
            # Native inference owns its model until close succeeds.
            unload = getattr(self.inference, 'unload', None)
            if unload is None:
                if self.inference.state() == 'loaded':
                    raise AppError('render_handoff')
            else:
                unload()
            with self.store.connection(write=True) as db:
                job = self._job(db, jid)
                if job['state'] != 'queued':
                    return
                if not self._fresh(db, job):
                    raise AppError('render_stale')
                dirty = db.execute('SELECT * FROM render_handoff').fetchone()
                if dirty and (dirty['renderer_key'] != self.renderer.key or dirty['phase'] != 0):
                    raise AppError('render_handoff')
                new_handoff = db.execute(
                    'INSERT OR IGNORE INTO render_handoff(singleton,renderer_key) VALUES (1,?)',
                    (self.renderer.key,)).rowcount == 1
                self._transition(db, jid, 'submitting')
            handle = self.renderer.submit(workflow.render(job['description'], jid), jid)
            with self.store.connection(write=True) as db:
                db.execute('UPDATE render_jobs SET renderer_id=? WHERE id=?', (handle, jid))
                latest = self._job(db, jid)
                self._transition(db, jid, 'cancel_requested' if latest['discard_reason'] else 'running')
        except AppError as error:
            with self.store.connection(write=True) as db:
                current = self._job(db, jid)
                if current['state'] in {'queued', 'submitting'}:
                    uncertain = current['state'] == 'submitting' and error.code != 'render_rejected'
                    outcome = 'uncertain' if uncertain else 'cancelled' if error.code == 'render_stale' else 'failed'
                    self._transition(db, jid, outcome, 'render_uncertain' if uncertain else error.code)
                    if error.code == 'render_rejected' and new_handoff:
                        db.execute('DELETE FROM render_handoff')

    def _finish(self, jid, state, error=None, image=None):
        saved = None
        try:
            with self.store.connection(write=True) as db:
                job = self._job(db, jid)
                if job['state'] in TERMINAL:
                    return
                fresh = self._fresh(db, job)
                if job['discard_reason'] or not fresh:
                    state = 'cancelled'
                    error = 'render_stale' if not fresh else None
                if state == 'succeeded':
                    identity = self._identity(db, job['conversation_id'])
                    try:
                        workflow_matches = self._workflow(identity['configuration']).digest == job['workflow_digest']
                    except AppError:
                        workflow_matches = False
                    if not workflow_matches:
                        self._transition(db, jid, 'cancelled', 'render_stale')
                        return
                    saved = self.assets.save(*image)
                    asset, media, size, width, height, checksum = saved
                    db.execute('''INSERT INTO visual_assets(id,conversation_id,job_id,media_type,bytes,width,height,checksum)
                                  VALUES (?,?,?,?,?,?,?,?)''',
                               (asset, job['conversation_id'], jid, media, size, width, height, checksum))
                self._transition(db, jid, state, error)
        except AppError:
            if saved:
                self.assets.discard(saved[0])
            raise

    def _reconcile(self, job):
        jid = job['id']
        try:
            self._matching_renderer(job)
            handle = job['renderer_id'] or self.renderer.locate(jid)
            if not handle:
                raise AppError('render_uncertain')
            with self.store.connection(write=True) as db:
                current = self._job(db, jid)
                stale = not self._fresh(db, current)
                discard = current['discard_reason'] or ('stale' if stale else None)
                db.execute('UPDATE render_jobs SET renderer_id=?,discard_reason=? WHERE id=?', (handle, discard, jid))
            state, output = self.renderer.poll(handle, jid, None if discard else job['output_node'])
            if state == 'queued' and discard and self.renderer.cancel_owned(handle, jid):
                self._finish(jid, 'cancelled')
            elif state == 'missing':
                raise AppError('render_uncertain')
            elif state in ('running', 'queued'):
                target = 'cancel_requested' if discard else 'running'
                if target != job['state']:
                    with self.store.connection(write=True) as db:
                        self._transition(db, jid, target)
            elif state == 'failed' or discard:
                self._finish(jid, 'failed', 'render_failed')
            elif state == 'succeeded':
                self._finish(jid, 'succeeded', image=self.renderer.fetch(output))
        except AppError as error:
            if error.code in {'asset_invalid', 'asset_unavailable'}:
                self._finish(jid, 'failed', error.code)
            elif error.code != 'persistence_failed':
                if job['state'] != 'uncertain':
                    with self.store.connection(write=True) as db:
                        self._transition(db, jid, 'uncertain', 'render_uncertain')

    def step(self):
        active = self._select()
        if not active and self.chat_pending.is_set():
            return
        candidate = active if active else self._select(active=False)
        if candidate is None:
            with self.resources.acquire('background', 'handoff', blocking=False) as acquired:
                if acquired and not self.chat_pending.is_set():
                    self._release_renderer()
            return
        kind = 'background' if candidate['kind'] == 'automatic' else 'manual'
        with self.resources.acquire(kind, candidate['id'], blocking=False) as acquired:
            if not acquired:
                return
            if active:
                self._reconcile(active)
            elif not self.chat_pending.is_set():
                # Recheck scheduling after claiming the lease so newly queued manual
                # work outranks an automatic candidate selected before the claim.
                latest = self._select(active=False)
                if latest:
                    self._begin(latest['id'])

    def _handoff_row(self):
        with self.store.connection() as db:
            return db.execute('SELECT * FROM render_handoff').fetchone() if db else None

    def _release_renderer(self):
        row = self._handoff_row()
        if row is None:
            return
        self._matching_renderer(row)
        if row['phase'] == 0:
            self.renderer.release_owned_resources()
        # /free sets async worker flags. The worker applies them between jobs.
        # Two serial, model-free previews after /free prove it crossed that boundary.
        for phase in range(max(1, row['phase']), 3):
            current = self._handoff_row()
            barrier = current['barrier_id'] or str(uuid4())
            handle = barrier
            if current['barrier_id'] is None:
                with self.store.connection(write=True) as db:
                    db.execute('UPDATE render_handoff SET phase=?,barrier_id=?', (phase, barrier))
                handle = self.renderer.submit(BARRIER, barrier)
            else:
                handle = self.renderer.locate(barrier)
                if not handle:
                    raise AppError('render_handoff')
            deadline = monotonic() + 5
            while monotonic() < deadline:
                state, _ = self.renderer.poll(handle, barrier, None)
                if state == 'succeeded':
                    break
                if state in {'failed', 'missing'}:
                    raise AppError('render_handoff')
                sleep(0.1)
            else:
                raise AppError('render_handoff')
            with self.store.connection(write=True) as db:
                if phase == 2:
                    db.execute('DELETE FROM render_handoff')
                else:
                    db.execute('UPDATE render_handoff SET phase=2,barrier_id=NULL')

    def recover_handoff(self):
        with self.resources.acquire('manual', 'handoff-recovery', blocking=False) as acquired:
            if not acquired or self._select() is not None:
                raise AppError('render_handoff')
            row = self._handoff_row()
            if not row:
                return
            self._matching_renderer(row)
            if not self.renderer.idle():
                raise AppError('render_handoff')
            with self.store.connection(write=True) as db:
                db.execute('UPDATE render_handoff SET phase=0,barrier_id=NULL')
            self._release_renderer()

    @contextmanager
    def chat_lease(self, owner):
        self.chat_pending.set()
        try:
            while True:
                with self.resources.acquire('chat', owner):
                    active = self._select()
                    if active is None:
                        try:
                            self._release_renderer()
                        except AppError as error:
                            raise AppError('render_handoff') from error
                        yield
                        return
                    if active['state'] == 'uncertain' or self._worker is None:
                        raise AppError('render_handoff')
                # Leave the lease available to the worker reconciling this render.
                # The reservation prevents any unstarted image from overtaking chat.
                self._wake.set()
                sleep(0.25)
        finally:
            self.chat_pending.clear()
            self._wake.set()

    def start(self):
        if self.renderer is None:
            return
        with self._lock:
            if self._worker is None:
                self._worker = Thread(target=self._work, name='incanta-render', daemon=True)
                self._worker.start()

    def stop(self):
        self._closing.set()
        self._wake.set()
        if self._worker is not None:
            self._worker.join(timeout=12)

    def _work(self):
        while not self._closing.is_set():
            try:
                self.step()
            except AppError:
                pass
            self._wake.wait(0.5)
            self._wake.clear()

from dataclasses import replace
from io import BytesIO
import json
from uuid import uuid4

from PIL import Image

from companion_helpers import CompanionCase
from frontend_app import create_app


def png():
    stream = BytesIO()
    Image.new('RGB', (2, 2)).save(stream, format='PNG')
    return stream.getvalue()


class FakeRenderer:
    key = 'test-renderer'

    def __init__(self):
        self.online = True
        self.jobs = {}
        self.submissions = []
        self.releases = 0
        self.ambiguous = False

    def inspect_capabilities(self):
        from backend.errors import AppError
        if not self.online:
            raise AppError('renderer_unavailable')
        return 'synthetic'

    def validate_workflow(self, workflow):
        self.inspect_capabilities()

    def idle(self):
        return all(state != 'running' for state in self.jobs.values())

    def submit(self, graph, job_id):
        from backend.errors import AppError
        self.jobs[job_id] = 'succeeded'
        self.submissions.append(job_id)
        if self.ambiguous:
            self.ambiguous = False
            raise AppError('render_uncertain')
        return job_id

    def locate(self, job):
        return job if job in self.jobs else None

    def poll(self, handle, job, output_node):
        self.inspect_capabilities()
        return self.jobs.get(handle, 'missing'), {'synthetic': True}

    def fetch(self, descriptor):
        return png(), 'image/png'

    def cancel_owned(self, handle, job):
        return False

    def release_owned_resources(self):
        self.inspect_capabilities()
        self.releases += 1


class RenderJobsTests(CompanionCase):
    def setUp(self):
        super().setUp()
        from pathlib import Path
        self.root = self.root.resolve()
        self.renderer = FakeRenderer()
        self.profile = self.root / 'workflows'
        self.profile.mkdir()
        self.output = self.root / 'assets'
        self.output.mkdir(mode=0o700)
        bundle = json.loads((Path(__file__).resolve().parents[1] /
                             'examples/render-workflow.example.json').read_text())
        (self.profile / 'synthetic.json').write_text(json.dumps(bundle))
        self.settings = replace(self.settings, workflow_root=self.profile, render_output_root=self.output)
        self.clock = 1000
        self.restart_visuals()

    def restart_visuals(self):
        self.app = create_app(self.settings, inference=self.fake, renderer=self.renderer,
                              visual_autostart=False, visual_clock=lambda: self.clock)
        self.client = self.app.test_client()
        self.token = self.client.get('/api/bootstrap').get_json()['csrf_token']
        self.visuals = self.app.extensions['incanta_visuals']

    def ready_chat(self, title='Synthetic'):
        cid = self.create(title)['id']
        result = self.call('PUT', f'/api/conversations/{cid}/visuals',
                           {'revision': 1, 'configuration': 'synthetic'})
        self.assertEqual(result.status_code, 200, result.get_json())
        return cid

    def enqueue(self, cid, kind='portrait', key=None):
        result = self.call('POST', f'/api/conversations/{cid}/images',
                           {'kind': kind, 'description': 'Synthetic scene', 'request_id': key or str(uuid4())})
        self.assertEqual(result.status_code, 202, result.get_json())
        return result.get_json()

    def image_list(self, cid):
        response = self.call('GET', f'/api/conversations/{cid}/images')
        self.assertEqual(response.status_code, 200, response.get_json())
        return response.get_json()

    def test_approval_is_explicit_owned_and_survives_offline_restart(self):
        first, second = self.ready_chat(), self.ready_chat('Synthetic B')
        self.enqueue(first)
        self.visuals.step()
        self.visuals.step()
        result = self.image_list(first)
        asset = result['jobs'][0]['asset_id']
        self.assertIsNone(result['identity']['approved_portrait_asset'])
        self.assertEqual(self.call('POST', f'/api/conversations/{second}/portrait',
                                   {'asset_id': asset}).status_code, 404)
        self.assertEqual(self.call('POST', f'/api/conversations/{first}/portrait',
                                   {'asset_id': asset}).status_code, 200)
        self.visuals.step()
        self.renderer.online = False
        self.restart_visuals()
        self.assertEqual(self.image_list(first)['identity']['approved_portrait_asset'], asset)
        self.assertEqual(self.image_list(second)['jobs'], [])
        image = self.call('GET', f'/api/assets/{asset}')
        self.assertEqual(image.data, png())
        self.assertEqual(image.headers['Cache-Control'], 'no-store')
        path = self.output / asset
        path.unlink()
        target = self.root / 'synthetic-target'
        target.write_bytes(png())
        path.symlink_to(target)
        self.assertEqual(self.call('GET', f'/api/assets/{asset}').status_code, 503)

    def test_duplicate_uncertain_submit_resolves_after_restart(self):
        cid = self.ready_chat()
        request_id = str(uuid4())
        jobs = [self.enqueue(cid, key=request_id)['id'] for _ in range(10)]
        self.assertEqual(len(set(jobs)), 1)
        self.renderer.ambiguous = True
        self.visuals.step()
        self.assertEqual(self.image_list(cid)['jobs'][0]['state'], 'uncertain')
        self.restart_visuals()
        self.visuals.step()
        self.assertEqual(self.image_list(cid)['jobs'][0]['state'], 'succeeded')
        self.assertEqual(self.renderer.submissions.count(jobs[0]), 1)

    def test_queued_cancel_and_stale_publication(self):
        cid = self.ready_chat()
        first = self.enqueue(cid)
        cancelled = self.call('POST', f"/api/image-jobs/{first['id']}/cancel", {})
        self.assertEqual(cancelled.get_json()['state'], 'cancelled')
        second = self.enqueue(cid, 'manual')
        self.visuals.step()
        self.call('POST', f'/api/conversations/{cid}/facts', {'content': 'Synthetic fact'})
        self.visuals.step()
        jobs = self.image_list(cid)['jobs']
        self.assertEqual(jobs[0]['id'], second['id'])
        self.assertEqual(jobs[0]['error'], 'render_stale')
        self.assertIsNone(jobs[0]['asset_id'])

    def test_auto_defaults_off_coalesces_and_manual_takes_next_slot(self):
        cid = self.ready_chat()
        self.fake.unload = lambda: None
        first = self.turn({'id': cid}).get_json()['turn']
        self.visuals.propose(cid, first['id'], 'Synthetic park', 1)
        self.assertEqual(self.image_list(cid)['jobs'], [])
        endpoint = f'/api/conversations/{cid}/scene-policy'
        self.assertEqual(self.call('PATCH', endpoint, {
            'enabled': True, 'cooldown_seconds': 60, 'revision': 1}).status_code, 200)
        self.fake.reply = '{"reply":"Synthetic reply.","scene":"A synthetic park"}'
        new_turn = self.turn({'id': cid}).get_json()['turn']
        self.assertEqual(new_turn['response'], 'Synthetic reply.')
        self.fake.reply = '{"reply":"Synthetic reply.","scene":"A synthetic beach"}'
        self.turn({'id': cid})
        jobs = self.image_list(cid)['jobs']
        self.assertEqual([(job['kind'], job['description']) for job in jobs],
                         [('automatic', 'A synthetic beach')])
        auto = jobs[0]['id']
        manual = self.enqueue(cid, 'manual')['id']
        self.visuals.step()
        self.assertEqual(self.renderer.submissions, [manual])
        self.visuals.step()
        self.visuals.step()
        self.assertEqual(self.renderer.submissions, [manual, auto])
        self.visuals.step()
        self.fake.reply = '{"reply":"Synthetic reply.","scene":"A synthetic station"}'
        self.turn({'id': cid})
        self.assertEqual(len(self.image_list(cid)['jobs']), 2)
        self.clock += 60
        self.turn({'id': cid})
        queued = self.image_list(cid)['jobs'][0]
        self.assertEqual(queued['state'], 'queued')
        self.assertEqual(self.call('PATCH', endpoint, {
            'enabled': False, 'cooldown_seconds': 60, 'revision': 2}).status_code, 200)
        self.assertEqual(self.image_list(cid)['jobs'][0]['state'], 'cancelled')

    def test_lost_history_requires_explicit_resolution_without_resubmit(self):
        cid = self.ready_chat()
        job = self.enqueue(cid)
        self.visuals.step()
        self.renderer.jobs.clear()
        self.restart_visuals()
        self.visuals.step()
        self.assertEqual(self.image_list(cid)['jobs'][0]['state'], 'uncertain')
        self.visuals.step()
        self.assertEqual(self.renderer.submissions, [job['id']])
        endpoint = f"/api/image-jobs/{job['id']}/resolve"
        self.assertEqual(self.call('POST', endpoint, {}).status_code, 400)
        self.assertEqual(self.call('POST', endpoint, {'confirm_missing': True}).get_json()['state'], 'cancelled')

    def test_running_cancel_discards_result_and_disk_failure_keeps_portrait(self):
        from unittest.mock import patch

        cid = self.ready_chat()
        original = self.enqueue(cid)
        self.visuals.step()
        self.visuals.step()
        portrait = self.image_list(cid)['jobs'][0]['asset_id']
        self.assertIsNotNone(portrait)
        self.call('POST', f'/api/conversations/{cid}/portrait', {'asset_id': portrait})
        running = self.enqueue(cid, 'manual')
        self.visuals.step()
        self.renderer.jobs[running['id']] = 'running'
        result = self.call('POST', f"/api/image-jobs/{running['id']}/cancel", {})
        self.assertEqual(result.status_code, 202)
        self.assertFalse(result.get_json()['running_interrupt_supported'])
        self.visuals.step()
        self.assertEqual(self.image_list(cid)['jobs'][0]['state'], 'cancel_requested')
        self.renderer.jobs[running['id']] = 'succeeded'
        self.visuals.step()
        self.assertEqual(self.image_list(cid)['jobs'][0]['state'], 'cancelled')
        bad = self.enqueue(cid, 'manual')
        self.visuals.step()
        with patch('backend.rendering.assets.os.replace', side_effect=OSError('synthetic disk fault')):
            self.visuals.step()
        result = self.image_list(cid)
        self.assertEqual(result['jobs'][0]['id'], bad['id'])
        self.assertEqual(result['jobs'][0]['error'], 'asset_unavailable')
        self.assertEqual(result['jobs'][-1]['id'], original['id'])
        self.assertEqual(result['identity']['approved_portrait_asset'], portrait)
        self.assertEqual([path.name for path in self.output.iterdir()], [portrait])
        self.visuals.step()
        self.renderer.online = False
        self.assertEqual(self.turn({'id': cid}).status_code, 200)

    def test_queue_bounds_and_same_origin(self):
        cid = self.ready_chat()
        endpoint = f'/api/conversations/{cid}/images'
        body = {'kind': 'manual', 'description': 'Synthetic scene', 'request_id': str(uuid4())}
        self.assertEqual(self.client.post(endpoint, json=body).status_code, 403)
        for _ in range(5):
            self.enqueue(cid, 'manual')
        self.assertEqual(self.call('POST', endpoint, body).get_json()['error']['code'], 'render_queue_full')
        self.assertEqual(self.call('POST', endpoint, dict(body, description='a' * 2001)).status_code, 400)

    def test_handoff_failure_blocks_loading_until_owned_release(self):
        cid = self.ready_chat()
        self.enqueue(cid)
        self.visuals.step()
        self.visuals.step()
        self.renderer.online = False
        self.assertEqual(self.turn({'id': cid}).get_json()['error']['code'], 'render_handoff')
        self.assertEqual(self.fake.calls, 0)
        self.renderer.online = True
        self.assertEqual(self.turn({'id': cid}).status_code, 200)
        self.assertEqual(self.renderer.releases, 1)
        self.assertEqual(self.fake.calls, 1)

    def test_background_worker_waiting_chat_outranks_unstarted_image(self):
        from concurrent.futures import ThreadPoolExecutor
        from time import monotonic, sleep

        cid = self.ready_chat()
        order = []
        self.fake.unload = lambda: order.append('unload')
        generate = self.fake.generate
        self.fake.generate = lambda prompt: (order.append('chat'), generate(prompt))[1]
        first = self.enqueue(cid, 'manual')
        second = self.enqueue(cid, 'manual')
        submit = self.renderer.submit

        def delayed_submit(graph, job_id):
            handle = submit(graph, job_id)
            if job_id == first['id']:
                self.renderer.jobs[handle] = 'running'
            if job_id == second['id']:
                order.append('second')
            return handle

        def wait_until(predicate):
            deadline = monotonic() + 5
            while not predicate() and monotonic() < deadline:
                sleep(0.01)
            self.assertTrue(predicate())

        self.renderer.submit = delayed_submit
        self.visuals.start()
        self.addCleanup(self.visuals.stop)
        wait_until(lambda: self.renderer.jobs.get(first['id']) == 'running')
        with ThreadPoolExecutor() as executor:
            chat = executor.submit(self.app.extensions['incanta'].process, cid, 'Synthetic hello', str(uuid4()))
            try:
                wait_until(self.visuals.chat_pending.is_set)
                self.assertNotIn(second['id'], self.renderer.jobs)
            finally:
                self.renderer.jobs[first['id']] = 'succeeded'
            self.assertEqual(chat.result(timeout=8)['response'], self.fake.reply)
        wait_until(lambda: second['id'] in self.renderer.jobs)
        self.assertLess(order.index('chat'), order.index('second'))

    def test_existing_v1_conversation_survives_visual_migration(self):
        from contextlib import closing
        from pathlib import Path
        import sqlite3

        from backend.conversation_store import ConversationStore
        setup_path = Path(__file__).resolve().parents[1] / 'backend/migrations/001_companion.sql'
        path = self.settings.database_path
        path.parent.mkdir(parents=True)
        store = ConversationStore(path)
        with closing(sqlite3.connect(path)) as db:
            db.executescript(setup_path.read_text())
            from companion_helpers import SETUP
            cid = store.insert_conversation(db, SETUP)
            db.commit()
        self.assertEqual(self.image_list(cid)['jobs'], [])
        self.assertEqual(store.get_conversation(cid)['title'], SETUP['title'])
        with closing(sqlite3.connect(path)) as db:
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0], 2)

    def test_policy_toggle_invalidates_an_inflight_automatic_proposal(self):
        cid = self.ready_chat()
        endpoint = f'/api/conversations/{cid}/scene-policy'
        self.call('PATCH', endpoint, {'enabled': True, 'cooldown_seconds': 60, 'revision': 1})

        def generate(prompt):
            jobs = self.visuals
            jobs.set_policy(cid, {'enabled': False, 'cooldown_seconds': 60, 'revision': 2})
            jobs.set_policy(cid, {'enabled': True, 'cooldown_seconds': 60, 'revision': 3})
            return '{"reply":"Synthetic reply.","scene":"A synthetic park"}'

        self.fake.generate = generate
        result = self.turn({'id': cid})
        self.assertEqual(result.get_json()['response'], 'Synthetic reply.')
        self.assertEqual(self.image_list(cid)['jobs'], [])

    def test_manual_queued_during_workflow_validation_overtakes_automatic(self):
        from unittest.mock import patch

        cid = self.ready_chat()
        self.fake.unload = lambda: None
        self.call('PATCH', f'/api/conversations/{cid}/scene-policy',
                  {'enabled': True, 'cooldown_seconds': 60, 'revision': 1})
        self.fake.reply = '{"reply":"Synthetic reply.","scene":"A synthetic park"}'
        self.turn({'id': cid})
        manual = []

        def add_manual(workflow):
            if not manual:
                manual.append(self.enqueue(cid, 'manual')['id'])

        with patch.object(self.renderer, 'validate_workflow', side_effect=add_manual):
            self.visuals.step()
        self.assertEqual(self.renderer.submissions, [])
        self.visuals.step()
        self.assertEqual(self.renderer.submissions, manual)

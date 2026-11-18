/* Conversation-scoped portraits, scene history and image jobs. */
(function(root) {
  'use strict';
  const STATES = {
    queued: 'Queued', submitting: 'Submitting', running: 'Rendering',
    cancel_requested: 'Cancelling. If rendering has started, Incanta will discard the result when it ends.',
    failed: 'Failed', cancelled: 'Cancelled', succeeded: 'Complete',
    uncertain: 'Submission uncertain. Incanta is checking the renderer and will not send this request again.'
  };
  const ERRORS = {
    renderer_unconfigured: 'Local visuals haven’t been configured.',
    renderer_unavailable: 'ComfyUI is unavailable. Saved images are still visible.',
    renderer_incompatible: 'Check the local workflow and dedicated ComfyUI instance.',
    render_rejected: 'ComfyUI rejected the workflow.',
    render_failed: 'ComfyUI could not finish this image.',
    render_stale: 'The conversation or its visual identity changed.',
    asset_invalid: 'ComfyUI returned an invalid image.',
    asset_unavailable: 'Check access to the private image folder.',
    render_handoff: 'Check the renderer before retrying.'
  };

  function path(cid, suffix) {
    return `/api/conversations/${encodeURIComponent(cid)}/${suffix}`;
  }

  function assetPath(id) {
    return typeof id === 'string' && /^[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/.test(id)
      ? `/api/assets/${id}` : null;
  }

  function jobActions(job, approved) {
    if (['queued', 'submitting', 'running'].includes(job.state)) return ['cancel'];
    if (job.state === 'uncertain') return ['resolve'];
    if (['failed', 'cancelled'].includes(job.state) && job.kind !== 'automatic') return ['retry'];
    if (job.state === 'succeeded' && job.kind === 'portrait' && job.asset_id && job.asset_id !== approved) {
      return ['approve', 'reject'];
    }
    return [];
  }

  function createVisualClient(api, idFactory = () => root.crypto.randomUUID()) {
    let selected = null, generation = 0;
    const pending = new Map();
    return {
      get selected() { return selected; },
      select(cid) { selected = cid; generation += 1; },
      async list(cursor) {
        const snapshot = generation;
        const result = await api.request(path(selected, 'images') + (cursor ? `?cursor=${cursor}` : ''));
        return snapshot === generation ? result : null;
      },
      async submit(cid, kind, description) {
        const trimmed = description.trim();
        let submission = pending.get(cid);
        if (!submission || submission.kind !== kind || submission.description !== trimmed) {
          submission = {kind, description: trimmed, request_id: idFactory()};
          pending.set(cid, submission);
        }
        const result = await api.mutate(path(cid, 'images'), 'POST', submission);
        if (pending.get(cid) === submission) pending.delete(cid);
        return result;
      }
    };
  }

  function mount(document, api) {
    const client = createVisualClient(api);
    const get = id => document.getElementById(id);
    const notice = get('visual-error');
    const list = get('visual-jobs');
    const identityForm = get('visual-identity');
    const sceneForm = get('visual-request');
    const policyForm = get('visual-policy');
    let view = null, currentStatus = null, fingerprint = '', older = [], nextCursor = null;
    let pending = false, polling = false, pollVersion = 0, loadedEarlier = false, statusAt = 0;

    function showAsset(element, id) {
      const src = assetPath(id);
      element.hidden = !src;
      if (src && element.getAttribute('src') !== src) element.setAttribute('src', src);
      if (!src) element.removeAttribute('src');
    }

    function action(element, fn) {
      return async event => {
        event.preventDefault();
        if (pending || !client.selected || !view) return;
        const cid = client.selected;
        pending = true;
        element.disabled = true;
        try {
          await fn(cid);
          if (client.selected === cid) {
            notice.textContent = '';
            await refresh(true);
          }
        } catch (failure) {
          if (client.selected === cid) notice.textContent = failure.message;
        } finally {
          element.disabled = false;
          pending = false;
        }
      };
    }

    async function jobAction(cid, job, actionName) {
      const endpoint = `/api/image-jobs/${encodeURIComponent(job.id)}`;
      if (actionName === 'retry') return client.submit(cid, job.kind, job.description);
      if (actionName === 'cancel') return api.mutate(endpoint + '/cancel', 'POST', {});
      if (actionName === 'resolve') {
        if (!root.confirm('Confirm you restarted the dedicated ComfyUI renderer and checked that this request is missing.')) return;
        return api.mutate(endpoint + '/resolve', 'POST', {confirm_missing: true});
      }
      return api.mutate(path(cid, 'portrait'), 'POST', {asset_id: job.asset_id, decision: actionName});
    }

    function render() {
      const portrait = view.identity.approved_portrait_asset;
      showAsset(get('approved-portrait'), portrait);
      const jobs = [...view.jobs, ...older.filter(job => !view.jobs.some(recent => recent.id === job.id))];
      const signature = JSON.stringify([portrait, jobs]);
      if (signature !== fingerprint) {
        const buttons = {cancel:'Cancel', retry:'Retry', resolve:'Resolve missing request', approve:'Approve portrait', reject:'Reject portrait'};
        const rows = jobs.map(job => {
          const item = document.createElement('li');
          const label = document.createElement('p');
          const kind = {portrait:'Portrait', manual:'Scene', automatic:'Automatic scene'}[job.kind];
          label.textContent = `${kind} · ${STATES[job.state] || 'Unknown'} ${ERRORS[job.error] || ''}`.trim();
          item.append(label);
          if (job.asset_id && job.asset_id !== portrait) {
            const image = document.createElement('img');
            image.alt = kind + ' of Celeste';
            image.loading = 'lazy';
            showAsset(image, job.asset_id);
            item.append(image);
          }
          for (const name of jobActions(job, portrait)) {
            const button = document.createElement('button');
            button.type = 'button';
            button.textContent = buttons[name];
            button.addEventListener('click', action(button, cid => jobAction(cid, job, name)));
            item.append(button);
          }
          return item;
        });
        list.replaceChildren(...rows);
        fingerprint = signature;
      }
      get('visual-load-earlier').hidden = !nextCursor;
      const heavy = jobs.some(job => ['submitting', 'running', 'cancel_requested'].includes(job.state));
      get('visual-wait').textContent = heavy ? 'Chat will wait for the running image. Your reply takes priority over queued images.' : '';
      get('visual-submit').disabled = !view.identity.configuration || !currentStatus?.configured;
      policyForm.hidden = !view.identity.configuration;
      if (!identityForm.contains(document.activeElement)) {
        get('visual-configuration').value = view.identity.configuration || '';
      }
      if (!policyForm.contains(document.activeElement)) {
        get('visual-automatic').checked = view.policy.enabled;
        get('visual-cooldown').value = view.policy.cooldown_seconds;
      }
    }

    async function refresh(checkStatus = false) {
      if (!client.selected) return;
      const snapshot = ++pollVersion;
      const latest = await client.list();
      if (!latest || snapshot !== pollVersion) return;
      view = latest;
      if (!loadedEarlier) nextCursor = view.next_cursor;
      render();
      if (checkStatus) {
        const selection = view.identity.configuration;
        const query = selection ? `?configuration=${encodeURIComponent(selection)}` : '';
        const status = await api.request('/api/visuals/status' + query);
        if (snapshot !== pollVersion) return;
        currentStatus = status;
        statusAt = Date.now();
        get('visual-readiness').textContent = ERRORS[status.error] ||
          (status.compatible ? 'Local workflow is ready.' : 'Choose a configured visual profile.');
        get('visual-recover').hidden = !status.handoff_pending;
        render();
      }
    }

    identityForm.addEventListener('submit', action(get('visual-save-identity'), cid =>
      api.mutate(path(cid, 'visuals'), 'PUT', {revision:view.identity.revision,
        configuration:get('visual-configuration').value.trim() || null})));
    sceneForm.addEventListener('submit', action(get('visual-submit'), async cid => {
      await client.submit(cid, get('visual-kind').value, get('visual-description').value);
      if (client.selected === cid) get('visual-description').value = '';
    }));
    policyForm.addEventListener('submit', action(get('visual-save-policy'), cid =>
      api.mutate(path(cid, 'scene-policy'), 'PATCH', {revision:view.policy.revision,
        enabled:get('visual-automatic').checked, cooldown_seconds:Number(get('visual-cooldown').value)})));
    get('visual-load-earlier').addEventListener('click', action(get('visual-load-earlier'), async () => {
      const page = await client.list(nextCursor);
      if (!page) return;
      loadedEarlier = true;
      older.push(...page.jobs);
      nextCursor = page.next_cursor;
      render();
    }));
    get('visual-recover').addEventListener('click', action(get('visual-recover'), async () => {
      if (root.confirm('Confirm the dedicated ComfyUI queue is idle. Incanta will check resource release again.')) {
        await api.mutate('/api/visuals/recover-handoff', 'POST', {confirm_idle:true});
      }
    }));
    async function refreshSafely(status) {
      const cid = client.selected;
      try { await refresh(status); }
      catch (failure) { if (cid && client.selected === cid) notice.textContent = failure.message; }
    }
    root.setInterval(async () => {
      if (pending || polling || !client.selected) return;
      polling = true;
      try { await refreshSafely(Date.now() - statusAt > 15000); }
      finally { polling = false; }
    }, 2500);
    return {
      refresh: () => refreshSafely(true),
      select(cid) {
        if (cid !== client.selected) {
          client.select(cid);
          pollVersion += 1;
          view = null;
          currentStatus = null;
          statusAt = 0;
          fingerprint = '';
          older = [];
          loadedEarlier = false;
          nextCursor = null;
          for (const form of [identityForm, sceneForm, policyForm]) form.reset();
          list.replaceChildren();
          showAsset(get('approved-portrait'), null);
          get('visual-load-earlier').hidden = true;
          get('visual-recover').hidden = true;
          get('visual-submit').disabled = true;
          get('visual-wait').textContent = '';
          get('visual-readiness').textContent = '';
          notice.textContent = '';
        }
        if (cid) refreshSafely(true);
      }
    };
  }

  const api = {createVisualClient, jobActions, assetPath, mount};
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.IncantaVisuals = api;
})(typeof globalThis === 'object' ? globalThis : this);

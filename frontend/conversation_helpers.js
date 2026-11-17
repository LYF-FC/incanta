/* Conversation transport: explicit retries, request identity, stale-view protection. */
(function(root) {
  'use strict';
  function createClient(fetchImpl, idFactory = () => root.crypto.randomUUID()) {
    let token = '', selectedId = null, generation = 0, busy = false, selecting = false;
    const pending = new Map();
    async function request(path, options) {
      try {
        const response = await fetchImpl(path, {credentials:'same-origin', ...options});
        const payload = await response.json();
        if (!response.ok) throw {controlled:true, message:payload?.error?.message || 'The request could not be completed. Refresh and try again.'};
        return payload;
      } catch(error) {
        throw new Error(error?.controlled ? error.message : 'The local app could not complete this request. Check the connection and retry.');
      }
    }
    async function mutate(path, method, body) {
      return request(path, {method, headers:{'Content-Type':'application/json','X-CSRF-Token':token}, body:JSON.stringify(body)});
    }
    return {
      get selectedId() {return selectedId;},
      get busy() {return busy;},
      get selecting() {return selecting;},
      request, mutate,
      async initialize() {const value = await request('/api/bootstrap');token = value.csrf_token;return value;},
      clear() {selectedId = null;generation += 1;selecting = false;},
      async select(id) {
        const snapshot = ++generation;selecting = true;
        try {
          const result = await request(`/api/conversations/${encodeURIComponent(id)}`);
          if (snapshot !== generation) return null;
          selectedId = id;
          return result;
        } catch(error) {
          if (snapshot !== generation) return null;
          throw error;
        } finally {if (snapshot === generation) selecting = false;}
      },
      async send(message) {
        if (busy || selecting || !selectedId || typeof message !== 'string' || !message.trim()) throw new Error('Choose a conversation and wait for it to load or finish replying.');
        const cid = selectedId, snapshot = generation, trimmed = message.trim();
        let submission = pending.get(cid);
        if (!submission || submission.message !== trimmed) {
          submission = {message:trimmed, request_id:idFactory()};pending.set(cid, submission);
        }
        busy = true;
        try {
          const result = await mutate(`/api/conversations/${cid}/turns`, 'POST', submission);
          if (typeof result.response !== 'string') throw new Error('The local reply could not be read. Retry to retrieve the saved turn.');
          pending.delete(cid);
          return {...result, applies:snapshot === generation && selectedId === cid};
        } finally {busy = false;}
      }
    };
  }
  const api = {createClient};
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.IncantaConversations = api;
})(typeof globalThis === 'object' ? globalThis : this);

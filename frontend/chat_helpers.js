/* Small browser/Node shared helpers. No HTML parsing of conversation text. */
(function (root) {
  'use strict';
  function appendMessage(document, container, sender, message) {
    const bubble = document.createElement('div');
    bubble.classList.add('chat-bubble', sender);
    const text = document.createElement('span');
    text.textContent = String(message);
    bubble.appendChild(text);
    container.appendChild(bubble);
    container.scrollTop = container.scrollHeight;
  }

  function createChatController({fetchImpl, onMessage, onState, onError, onBusy}) {
    let pending = false;
    return {
      async send(message) {
        if (pending || typeof message !== 'string' || !message.trim()) return false;
        pending = true;
        onBusy(true);
        try {
          onMessage('user', message.trim());
          const response = await fetchImpl('/api/chat', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body:JSON.stringify({message:message.trim()})
          });
          const payload = await response.json();
          if (!response.ok) {
            onError(typeof payload?.error?.message === 'string' ? payload.error.message : 'The reply could not be completed. Try again.');
            return false;
          }
          if (typeof payload?.response !== 'string' || typeof payload?.emotion !== 'string'
              || !payload.gauges || typeof payload.gauges !== 'object') {
            throw new Error('invalid response');
          }
          onMessage('celeste', payload.response);
          onState(payload);
          onError('');
          return true;
        } catch {
          onError('The local app could not complete the request. Check the connection and try again.');
          return false;
        } finally {
          pending = false;
          onBusy(false);
        }
      }
    };
  }
  const api = {appendMessage, createChatController};
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.IncantaChat = api;
})(typeof globalThis === 'object' ? globalThis : this);

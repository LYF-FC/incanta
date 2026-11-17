(function(root) {
  'use strict';
  function textElement(document, tag, text) {
    const element = document.createElement(tag);element.textContent = String(text);return element;
  }
  function render({document, container, facts, conversations, conversationId, mutate, refresh, onError}) {
    container.replaceChildren();
    if (!facts.length) container.appendChild(textElement(document,'p','No saved facts in this conversation.'));
    for (const fact of facts) {
      const card = document.createElement('article');card.className = 'memory-card';
      card.appendChild(textElement(document,'p',fact.source_conversation_id === conversationId ?
        (fact.source_turn_id ? 'Saved from an exchange in this conversation.' : 'Owner-saved note.') : 'Explicitly shared from another conversation.'));
      const label = textElement(document,'label','Memory text');
      const field = document.createElement('textarea');field.value = fact.content;field.maxLength = 2000;field.required = true;
      label.appendChild(field);card.appendChild(label);
      const act = (title, operation) => {
        const button = textElement(document,'button',title);button.type = 'button';
        button.addEventListener('click',async()=>{
          button.disabled = true;
          try {await operation();await refresh();onError('');}
          catch(error) {onError(error.message);}
          finally {button.disabled = false;}
        });card.appendChild(button);
      };
      act('Save correction',()=>mutate(`/api/facts/${fact.id}`,'PATCH',{revision:fact.revision,content:field.value}));
      act('Delete memory',()=>mutate(`/api/facts/${fact.id}`,'DELETE',{revision:fact.revision}));
      const shareLabel = textElement(document,'label','Share this selected fact with');
      const recipients = document.createElement('select');
      recipients.setAttribute('aria-label','Share this selected fact with');
      recipients.appendChild(textElement(document,'option','Choose a conversation'));
      recipients.firstChild.value = '';
      for (const conversation of conversations) {
        if (conversation.id === conversationId || conversation.id === fact.source_conversation_id) continue;
        const option = textElement(document,'option',conversation.title);option.value = conversation.id;recipients.appendChild(option);
      }
      shareLabel.appendChild(recipients);card.appendChild(shareLabel);
      act('Share selected fact',()=>{
        if (!recipients.value) throw new Error('Choose a conversation to share with.');
        return mutate(`/api/facts/${fact.id}/grants/${recipients.value}`,'PUT',{revision:fact.revision});
      });
      for (const cid of fact.shared_recipients) {
        const name = conversations.find(c=>c.id === cid)?.title || 'Shared conversation';
        act(`Stop sharing with ${name}`,()=>mutate(`/api/facts/${fact.id}/grants/${cid}`,'DELETE',{revision:fact.revision}));
      }
      container.appendChild(card);
    }
  }
  const api = {textElement,render};
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.IncantaMemory = api;
})(typeof globalThis === 'object' ? globalThis : this);

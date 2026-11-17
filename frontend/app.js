'use strict';
const byId = id => document.getElementById(id);
const client = IncantaConversations.createClient((...args)=>fetch(...args));
let conversations = [], current = null, editing = false, previewToken = null, memoryRevision = 0;
const error = message => {byId('chat-error').textContent = message;};
const textNode = (tag,text)=>IncantaMemory.textElement(document,tag,text);
function selectedStorage(id) {try {if(id)localStorage.setItem('incanta.selectedConversation',id);else localStorage.removeItem('incanta.selectedConversation');} catch { /* Optional selection convenience. */ }}
function setupValues() {
  return Object.fromEntries(['title','personality','relationship','boundaries'].map(key=>[key,byId(`setup-${key}`).value]));
}
function showSetup(value) {
  editing = Boolean(value);byId('setup-panel').hidden = false;
  byId('setup-heading').textContent = value ? 'Edit this conversation' : 'Set up a conversation';
  byId('save-setup').textContent = value ? 'Save setup' : 'Create conversation';
  byId('cancel-setup').hidden = !current;
  for(const key of ['title','personality','relationship','boundaries']) byId(`setup-${key}`).value = value?.[key] || '';
}
async function listConversations() {
  conversations = (await client.request('/api/conversations')).conversations;
  const select = byId('conversation-select');select.replaceChildren();
  const placeholder = textNode('option',conversations.length ? 'Choose a conversation' : 'Create your first conversation');placeholder.value = '';select.appendChild(placeholder);
  for(const conversation of conversations) {const option = textNode('option',conversation.title);option.value = conversation.id;select.appendChild(option);}
  select.value = client.selectedId || '';
}
function renderState(state) {
  byId('emotion-label').textContent = `Current emotion: ${state.emotion}`;
  const container = byId('gauge-container');container.replaceChildren();
  for(const [name,value] of Object.entries(state.gauges)) {
    const line = textNode('div',`${name}: ${Math.max(0,Math.min(100,value))}`);line.className = 'gauge-value';container.appendChild(line);
  }
}
function renderTranscript() {
  const messages = byId('chat-messages');messages.replaceChildren();
  const sources = byId('memory-source');sources.replaceChildren();const note = textNode('option','Owner note');note.value = '';sources.appendChild(note);
  for(const turn of current.turns) {
    IncantaChat.appendMessage(document,messages,'user',turn.input);
    IncantaChat.appendMessage(document,messages,'celeste',turn.response);
    const option = textNode('option',`Exchange: ${turn.input.slice(0,65)}`);option.value = turn.id;sources.appendChild(option);
  }
  byId('load-earlier').hidden = !current.next_cursor;
}
async function refreshMemories() {
  const cid = client.selectedId;if(!cid)return;
  const version = ++memoryRevision;
  const result = await client.request(`/api/conversations/${cid}/facts`);
  if(client.selectedId !== cid || version !== memoryRevision)return;
  IncantaMemory.render({document,container:byId('memory-list'),facts:result.facts,conversations,conversationId:cid,
    mutate:client.mutate,refresh:refreshMemories,onError:error});
}
async function selectConversation(cid) {
  const result = await client.select(cid);if(!result)return;
  current = result;selectedStorage(cid);
  byId('conversation-select').value = cid;
  byId('conversation-panel').hidden = false;byId('setup-panel').hidden = true;byId('edit-settings').disabled = false;
  byId('conversation-heading').textContent = result.title;
  byId('effective-settings').textContent = `Personality: ${result.personality}\nRelationship: ${result.relationship || 'Not specified'}\nBoundaries: ${result.boundaries}`;
  renderState(result.state);renderTranscript();await refreshMemories();
}
async function refreshStatus() {
  const state = await client.request('/api/status');
  const issues = {model_unavailable:'Connect or configure the local model.',invalid_configuration:'Check local settings.',storage_unavailable:'Check conversation storage access.',history_unreadable:'Preserve the unreadable database for repair.'};
  byId('readiness-label').textContent = state.ready ? 'Ready to chat.' : state.issues.map(code=>issues[code] || 'Check the local app settings.').join(' ');
}
async function initialize() {
  const bootstrap = await client.initialize();byId('import-panel').hidden = !bootstrap.legacy_import_configured;
  await listConversations();await refreshStatus();
  let saved = null;try {saved = localStorage.getItem('incanta.selectedConversation');} catch { /* Optional. */ }
  const target = conversations.find(c=>c.id === saved) || conversations[0];
  if(target)await selectConversation(target.id);else showSetup(null);
}
function action(handler) {return async event=>{event.preventDefault();try {await handler(event);error('');} catch(caught) {error(caught.message);}};}
byId('refresh-status').addEventListener('click',action(async()=>{await client.initialize();await refreshStatus();await listConversations();}));
byId('new-conversation').addEventListener('click',()=>{client.clear();current = null;selectedStorage(null);byId('conversation-panel').hidden = true;byId('edit-settings').disabled = true;byId('conversation-select').value = '';showSetup(null);});
byId('edit-settings').addEventListener('click',()=>{if(current)showSetup(current);});
byId('cancel-setup').addEventListener('click',()=>{byId('setup-panel').hidden = true;});
byId('conversation-select').addEventListener('change',action(async event=>{if(event.target.value)await selectConversation(event.target.value);}));
byId('setup-form').addEventListener('submit',action(async()=>{
  const values = setupValues();
  const result = editing && current ? await client.mutate(`/api/conversations/${current.id}/settings`,'PATCH',{...values,settings_revision:current.settings_revision}) : await client.mutate('/api/conversations','POST',values);
  await listConversations();await selectConversation(result.id);
}));
byId('chat-form').addEventListener('submit',async event=>{
  event.preventDefault();if(client.busy)return;
  const input = byId('chat-input');const cid = client.selectedId;
  byId('send-button').disabled = true;input.disabled = true;byId('send-button').textContent = 'Replying…';
  try {
    const result = await client.send(input.value);
    if(result.applies && client.selectedId === cid) {input.value = '';await listConversations();if(client.selectedId === cid)await selectConversation(cid);error('');}
  } catch(caught) {error(caught.message);}
  finally {byId('send-button').disabled = false;input.disabled = false;byId('send-button').textContent = 'Send';input.focus();}
});
byId('toggle-gauges').addEventListener('click',event=>{const show = byId('gauge-container').hidden;byId('gauge-container').hidden = !show;event.target.textContent = show ? 'Hide gauges' : 'Show gauges';event.target.setAttribute('aria-expanded',String(show));});
byId('memory-form').addEventListener('submit',action(async()=>{
  const cid = client.selectedId;if(!cid)return;
  await client.mutate(`/api/conversations/${cid}/facts`,'POST',{content:byId('memory-text').value,source_turn_id:byId('memory-source').value || null});
  byId('memory-text').value = '';await refreshMemories();
}));
byId('load-earlier').addEventListener('click',action(async()=>{
  if(!current?.next_cursor)return;
  const cid = current.id, cursor = current.next_cursor;
  const result = await client.request(`/api/conversations/${cid}?cursor=${cursor}`);
  if(current?.id !== cid || current.next_cursor !== cursor)return;
  current.turns = [...result.turns,...current.turns];current.next_cursor = result.next_cursor;renderTranscript();
}));
byId('preview-import').addEventListener('click',action(async()=>{
  const result = await client.mutate('/api/imports/preview','POST',{selection:'configured',setup:setupValues()});
  previewToken = result.preview_token;byId('import-preview').textContent = `${result.turn_count} exchanges will be imported into “${result.setup.title}”. ${result.warnings.join(' ')}`;byId('confirm-import').hidden = false;
}));
byId('confirm-import').addEventListener('click',action(async()=>{
  const result = await client.mutate('/api/imports/confirm','POST',{preview_token:previewToken});
  previewToken = null;byId('confirm-import').hidden = true;byId('import-preview').textContent = 'Import saved. Original bytes preserved locally.';await listConversations();await selectConversation(result.id);
}));
initialize().catch(caught=>error(caught.message));

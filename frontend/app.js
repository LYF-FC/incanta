'use strict';
const form = document.getElementById('chat-form');
const input = document.getElementById('chat-input');
const sendButton = document.getElementById('send-button');
const messages = document.getElementById('chat-messages');
const errorLabel = document.getElementById('chat-error');
const readiness = document.getElementById('readiness-label');
let lastGaugeValues = {};
let stateRevision = 0;

function updateState(state) {
  document.getElementById('emotion-label').textContent = `Current Emotion: ${state.emotion}`;
  for (const [name,value] of Object.entries(state.gauges)) {
    const bar = document.getElementById(`gauge-${name}`);
    if (!bar || !Number.isFinite(value)) continue;
    const bounded = Math.max(0, Math.min(100, value));
    bar.style.width = `${bounded}%`;
    bar.textContent = `${name}: ${bounded}`;
    bar.classList.remove('green-flash','red-flash');
    if (name in lastGaugeValues && bounded !== lastGaugeValues[name]) {
      void bar.offsetWidth;
      bar.classList.add(bounded > lastGaugeValues[name] ? 'green-flash' : 'red-flash');
    }
    lastGaugeValues[name] = bounded;
  }
}
const issues = {
  model_unavailable:'Connect or configure a local model.',
  personality_unavailable:'Choose a valid character file.',
  invalid_configuration:'Check the local app settings.',
  storage_unavailable:'Check access to your conversation storage.',
  history_unreadable:'Preserve the unreadable history for repair.'
};
const chat = IncantaChat.createChatController({
  fetchImpl: (...args) => fetch(...args),
  onMessage: (sender,message) => IncantaChat.appendMessage(document,messages,sender,message),
  onState: state => { stateRevision += 1; updateState(state); },
  onError: message => { errorLabel.textContent = message; },
  onBusy: busy => {
    sendButton.disabled = busy;
    input.disabled = busy;
    form.setAttribute('aria-busy', String(busy));
    sendButton.textContent = busy ? 'Replying…' : 'Send';
  }
});
form.addEventListener('submit', async event => {
  event.preventDefault();
  const message = input.value;
  if (await chat.send(message)) input.value = '';
  input.focus();
});
document.getElementById('toggle-gauges').addEventListener('click', event => {
  const gauges = document.getElementById('gauge-container');
  const visible = gauges.style.display !== 'none';
  gauges.style.display = visible ? 'none' : 'flex';
  event.currentTarget.textContent = visible ? 'Show Gauges' : 'Hide Gauges';
  event.currentTarget.setAttribute('aria-expanded', String(!visible));
});
async function refreshStatus() {
  const revision = stateRevision;
  try {
    const response = await fetch('/api/status');
    const state = await response.json();
    if (!response.ok || !state.gauges || typeof state.emotion !== 'string') throw new Error('status');
    if (revision === stateRevision) updateState(state);
    readiness.textContent = state.ready ? 'Ready to chat.' : (state.issues || []).map(code => issues[code] || 'Check the local app.').join(' ');
  } catch {
    readiness.textContent = 'The local app is unavailable. Check the connection and try again.';
  }
}
refreshStatus();
document.getElementById('refresh-status').addEventListener('click', refreshStatus);

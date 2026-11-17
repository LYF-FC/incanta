const test = require('node:test');
const assert = require('node:assert/strict');
const { appendMessage, createChatController } = require('../frontend/chat_helpers.js');

function element() {
  return { children: [], classList: { add() {} }, textContent: '',
    appendChild(child) { this.children.push(child); },
    set innerHTML(value) { throw new Error('unsafe HTML'); } };
}
const document = { createElement: element };

test('user and model markup is inserted as literal text nodes', () => {
  const container = element();
  for (const role of ['user','celeste']) {
    const markup = '<img src=x onerror="window.unwanted=true">';
    appendMessage(document, container, role, markup);
    assert.equal(container.children.at(-1).children[0].textContent, markup);
  }
});

function controller(fetchImpl) {
  const events = [];
  return { events, chat: createChatController({ fetchImpl,
    onMessage: (...values) => events.push(['message',...values]),
    onState: value => events.push(['state',value]),
    onError: value => events.push(['error',value]),
    onBusy: value => events.push(['busy',value]) }) };
}
const success = () => ({ok:true, json:async()=>({response:'synthetic',emotion:'Neutral',gauges:{Trust:0}})});

test('successful chat applies returned state and restores input', async () => {
  const {chat, events} = controller(async()=>success());
  assert.equal(await chat.send(' hello '), true);
  assert.ok(events.some(event=>event[0]==='state'));
  assert.deepEqual(events.at(-1), ['busy',false]);
});

test('server failure displays error without treating it as a response and permits retry', async () => {
  let fail = true;
  const {chat,events} = controller(async()=>fail ? {ok:false,json:async()=>({error:{message:'Synthetic unavailable'}})} : success());
  assert.equal(await chat.send('hello'), false);
  assert.ok(events.some(event=>event[0]==='error' && event[1]==='Synthetic unavailable'));
  assert.equal(events.filter(event=>event[0]==='state').length,0);
  fail=false;
  assert.equal(await chat.send('retry'), true);
});

test('network errors and malformed replies restore controls without raw exceptions', async () => {
  for (const fetchImpl of [async()=>{throw Error('/private/synthetic')}, async()=>({ok:true,json:async()=>{throw Error('broken')}}), async()=>({ok:true,json:async()=>({})})]) {
    const {chat,events} = controller(fetchImpl);
    assert.equal(await chat.send('hello'), false);
    assert.deepEqual(events.at(-1), ['busy',false]);
    assert.equal(JSON.stringify(events).includes('/private'),false);
  }
});

test('in-flight duplicate submissions produce one fetch and no automatic retry', async () => {
  let resolve, calls=0;
  const {chat} = controller(()=>{calls++; return new Promise(done=>resolve=done);});
  const first=chat.send('hello');
  assert.equal(await chat.send('second'),false);
  assert.equal(calls,1);
  resolve(success());
  await first;
  assert.equal(calls,1);
});

test('blank submissions never call the server', async () => {
  let calls=0;
  const {chat}=controller(async()=>{calls++;return success();});
  assert.equal(await chat.send('  '),false);
  assert.equal(calls,0);
});

'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { createClient } = require('../frontend/conversation_helpers.js');
const reply = data => ({ok:true,json:async()=>data});

test('bootstrap CSRF token is included in mutations without logging private payloads', async()=>{
  const calls=[];
  const client=createClient(async(path,options)=>{calls.push([path,options]);return reply(path==='/api/bootstrap'?{csrf_token:'synthetic-token'}:{id:'synthetic-a',turns:[]});},()=> 'synthetic-request');
  await client.initialize(); await client.mutate('/api/conversations','POST',{title:'synthetic'});
  assert.equal(calls[1][1].headers['X-CSRF-Token'],'synthetic-token');
  assert.equal(calls[1][1].credentials,'same-origin');
});

test('switching chats prevents an earlier delayed response from selecting the wrong chat',async()=>{
  let finish;
  const client=createClient(path=>path.endsWith('/a')?new Promise(resolve=>{finish=()=>resolve(reply({id:'a'}));}):Promise.resolve(reply({id:'b'})));
  const a=client.select('a'); const b=await client.select('b');finish();
  assert.equal(b.id,'b');assert.equal(await a,null);assert.equal(client.selectedId,'b');
});

test('explicit retry after uncertain network failure reuses the request identifier',async()=>{
  let fail=true;const requests=[];
  const client=createClient(async(path,options)=>{
    if(!options?.method)return reply({id:'a'});
    requests.push(JSON.parse(options.body));
    if(fail)throw Error('/private/synthetic');
    return reply({response:'synthetic',conversation_id:'a'});
  },()=> 'request-one');
  await client.select('a');
  await assert.rejects(client.send('hello'),error=>!error.message.includes('/private'));
  fail=false;await client.send('hello');
  assert.equal(requests[0].request_id,requests[1].request_id);
});

test('send locks overlapping requests and marks a result obsolete after switching',async()=>{
  let finish,calls=0;
  const client=createClient((path,options)=>{
    if(!options?.method)return Promise.resolve(reply({id:path.split('/').at(-1)}));
    calls++;return new Promise(resolve=>{finish=()=>resolve(reply({response:'synthetic'}));});
  },()=> 'request');
  await client.select('a'); const first=client.send('hello');
  await assert.rejects(client.send('again'));
  await client.select('b');finish();
  assert.equal((await first).applies,false);assert.equal(calls,1);assert.equal(client.busy,false);
});

test('literal settings and memories use text nodes rather than HTML',()=>{
  const { textElement } = require('../frontend/memory_controls.js');
  const document={createElement:tag=>({tag,set innerHTML(value){throw Error('unsafe');}})};
  assert.equal(textElement(document,'span','<img src=x>').textContent,'<img src=x>');
});

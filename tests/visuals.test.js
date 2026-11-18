'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const {createVisualClient, jobActions, assetPath} = require('../frontend/visuals.js');

test('keeps request id when the image response was lost', async () => {
  const calls = [];
  const service = {mutate: async (_path, _method, body) => {
    calls.push(body);
    if (calls.length === 1) throw new Error('lost response');
    return {state: 'queued'};
  }};
  let next = 0;
  const images = createVisualClient(service, () => String(++next));
  await assert.rejects(images.submit('first', 'portrait', ' portrait '));
  await images.submit('first', 'portrait', 'portrait');
  await images.submit('other', 'portrait', 'portrait');
  assert.deepEqual(calls.map(call => call.request_id), ['1', '1', '2']);
});

test('offers cancellation or explicit resolution in the appropriate states', () => {
  assert.deepEqual(jobActions({state:'queued'}), ['cancel']);
  assert.deepEqual(jobActions({state:'running'}), ['cancel']);
  assert.deepEqual(jobActions({state:'cancel_requested'}), []);
  assert.deepEqual(jobActions({state:'failed',kind:'portrait'}), ['retry']);
  assert.deepEqual(jobActions({state:'uncertain'}), ['resolve']);
  assert.deepEqual(jobActions({state:'succeeded',kind:'portrait',asset_id:'image'}), ['approve','reject']);
  assert.equal(assetPath('../private'), null);
});

test('drops a late response after selecting another conversation', async () => {
  let finish;
  const api = {request: () => new Promise(resolve => {finish = resolve;})};
  const images = createVisualClient(api);
  images.select('first');
  const response = images.list();
  images.select('second');
  finish({jobs:[{id:'first-job'}]});
  assert.equal(await response, null);
});

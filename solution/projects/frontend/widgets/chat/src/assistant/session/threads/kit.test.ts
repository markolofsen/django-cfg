import assert from 'node:assert/strict';
import { test } from 'vitest';

import { ThreadNotFoundError } from '../../wire/transport';
import { fromStored } from '../stream/from-stored';
import { createChatTransport, loadChatAttachments, storedMessageOf, type ChatThreadCalls, type ChatMessageShape, type ChatTransportConfig } from './kit';
import { createSessionStorage } from './storage';

const MESSAGE: ChatMessageShape = {
  id: 'm1', seq: 1, role: 'assistant', text: 'hi', status: 'done', error_code: '',
  parts: [{ kind: 'citations', data: { items: [] } }], created_at: '2026-11-06T10:00:00Z',
};
const ROW = { id: 't1', title: 'T', updated_at: '2026-11-06T09:00:00Z' };

function calls(over: Partial<ChatThreadCalls> = {}): ChatThreadCalls {
  return {
    list: async () => ({ data: [{ ...ROW, message_count: 2, last_message_at: null }] }),
    create: async () => ({ data: ROW }),
    retrieve: async () => ({ data: { ...ROW, messages: [MESSAGE, { ...MESSAGE, id: 'm2', role: 'user', status: 'weird', error_code: 'busy' }] } }),
    ...over,
  };
}
const connect = (client: ChatThreadCalls, extra: Partial<Pick<ChatTransportConfig, 'kind' | 'trailingSlash' | 'buildBody' | 'getCreateContext' | 'hideEmpty'>> & { fetch?: typeof fetch } = {}) =>
  createChatTransport({ client, baseUrl: 'https://api.test', mount: '/apix/assistant', getToken: () => 'tok', streamFetch: extra.fetch, kind: extra.kind, trailingSlash: extra.trailingSlash, buildBody: extra.buildBody, getCreateContext: extra.getCreateContext, hideEmpty: extra.hideEmpty });

test('list maps rows; a null last_message_at falls back to updated_at', async () => {
  const [row] = await connect(calls()).api.list(new AbortController().signal);
  assert.deepEqual(row, { id: 't1', title: 'T', last_message_at: ROW.updated_at, message_count: 2 });
});

test('create sends the kind only when set, and returns a zero-count thread', async () => {
  const seen: unknown[] = [];
  const client = calls({ create: async (o) => (seen.push(o), { data: ROW }) });
  assert.equal((await connect(client).api.create()).message_count, 0);
  await connect(client, { kind: 'docs' }).api.create();
  assert.deepEqual(seen, [{}, { body: { kind: 'docs' } }]);
});

test('getCreateContext rides on create beside the kind, read per call; an empty result sends no context', async () => {
  const seen: unknown[] = [];
  const client = calls({ create: async (o) => (seen.push(o), { data: ROW }) });
  let doc: string | undefined = 'd1';
  const { api } = connect(client, { kind: 'docs', getCreateContext: () => (doc ? { document_id: doc } : undefined) });
  await api.create();
  doc = undefined;
  await api.create();
  assert.deepEqual(seen, [{ body: { kind: 'docs', context: { document_id: 'd1' } } }, { body: { kind: 'docs' } }]);
  await connect(client, { getCreateContext: () => ({ lang: 'ru' }) }).api.create();
  assert.deepEqual(seen[2], { body: { context: { lang: 'ru' } } });
});

test('hideEmpty drops threads with no messages from the list', async () => {
  const client = calls({ list: async () => ({ data: [{ ...ROW, message_count: 0, last_message_at: null }, { ...ROW, id: 't2', message_count: 3, last_message_at: null }] }) });
  const signal = new AbortController().signal;
  assert.equal((await connect(client).api.list(signal)).length, 2);
  assert.deepEqual((await connect(client, { hideEmpty: true }).api.list(signal)).map((t) => t.id), ['t2']);
});

test('buildBody reaches the stream request; absent, the default body is sent', async () => {
  const bodies: unknown[] = [];
  const fetchStub = (async (_url: string, init: RequestInit) => {
    bodies.push(JSON.parse(String(init.body)));
    return new Response('data: {"type":"done"}\n\n', { status: 200, headers: { 'content-type': 'text/event-stream' } });
  }) as unknown as typeof fetch;
  const input = { threadId: 't1', text: 'q', clientId: 'c', signal: new AbortController().signal };
  for (const buildBody of [undefined, (i: { text: string; clientId: string }) => ({ message: i.text, id: i.clientId, lang: 'ru' })]) {
    for await (const _ of connect(calls(), { fetch: fetchStub, buildBody }).transport.open(input)) void _;
  }
  assert.deepEqual(bodies, [{ text: 'q', client_id: 'c' }, { message: 'q', id: 'c', lang: 'ru' }]);
});

test('load maps messages: unknown status reads as error, empty error_code as null', async () => {
  const conversation = await connect(calls()).api.load('t1', new AbortController().signal);
  assert.equal(conversation.id, 't1');
  assert.deepEqual(conversation.messages[0]!.parts, [{ kind: 'citations', data: { items: [] } }]);
  assert.equal(conversation.messages[0]!.error_code, null);
  assert.equal(conversation.messages[1]!.status, 'error');
  assert.equal(conversation.messages[1]!.role, 'user');
  assert.equal(conversation.messages[1]!.error_code, 'busy');
});

test('a 404 is ThreadNotFoundError; any other failure is a plain error', async () => {
  const signal = new AbortController().signal;
  await assert.rejects(connect(calls({ retrieve: async () => ({ error: {}, response: { status: 404 } }) })).api.load('x', signal), ThreadNotFoundError);
  await assert.rejects(connect(calls({ retrieve: async () => ({ error: {}, response: { status: 500 } }) })).api.load('x', signal), (e) => !(e instanceof ThreadNotFoundError));
  await assert.rejects(connect(calls({ list: async () => ({}) })).api.list(signal));
});

test('the stream goes to <mount>/threads/<id>/messages/ with the bearer', async () => {
  const seen: Array<{ url: string; auth: string | null }> = [];
  const fetchStub = (async (url: string, init: RequestInit) => {
    seen.push({ url, auth: (init.headers as Record<string, string>).authorization ?? null });
    return new Response('data: {"type":"done"}\n\n', { status: 200, headers: { 'content-type': 'text/event-stream' } });
  }) as unknown as typeof fetch;
  for (const trailingSlash of [true, false]) {
    const { transport } = connect(calls(), { fetch: fetchStub, trailingSlash });
    for await (const _ of transport.open({ threadId: 'a b', text: 'q', clientId: 'c', signal: new AbortController().signal })) void _;
  }
  assert.deepEqual(seen, [
    { url: 'https://api.test/apix/assistant/threads/a%20b/messages/', auth: 'Bearer tok' },
    { url: 'https://api.test/apix/assistant/threads/a%20b/messages', auth: 'Bearer tok' },
  ]);
});

test('session storage remembers, forgets, and never throws', () => {
  const map = new Map<string, string>();
  const backing = { getItem: (k: string) => map.get(k) ?? null, setItem: (k: string, v: string) => void map.set(k, v), removeItem: (k: string) => void map.delete(k) };
  const s = createSessionStorage('app.session', backing);
  s.write('abc');
  assert.equal(s.read(), 'abc');
  s.write(null);
  assert.equal(s.read(), null);
  const broken = createSessionStorage('k', { getItem: () => { throw new Error('x'); }, setItem: () => { throw new Error('x'); }, removeItem: () => { throw new Error('x'); } });
  assert.equal(broken.read(), null);
  broken.write('a');
  broken.write(null);
});

const CTX = { signal: new AbortController().signal, onProgress: () => {} };

test('loadChatAttachments takes its limits from the server and uploads by the generated call', async () => {
  const cap = await loadChatAttachments({
    calls: {
      limits: async () => ({ data: { enabled: true, kinds: ['image', 'text', 'bogus'], accept: ['image/*'], max_files: 4, max_bytes: 100 } }),
      upload: async ({ body }) => (body.file.size > 5 ? { error: { code: 'too_large' }, response: { status: 413 } } : { data: { id: 'a', name: 'f', mime: 'text/plain', size: 1, kind: 'text', url: 'u' } }),
    },
    messages: { too_large: 'big' },
  });
  assert.deepEqual(cap?.kinds, ['image', 'text']);
  assert.equal(cap?.maxFileSize, 100);
  assert.equal(cap?.maxFiles, 4);
  assert.deepEqual(await cap!.upload(new File(['x'], 'f.txt'), CTX), { id: 'a', url: 'u' });
  await assert.rejects(cap!.upload(new File(['xxxxxxx'], 'f.txt'), CTX), (e: Error & { status?: number }) => e.message === 'big' && e.status === 413);
});

test('no attach control when the kind takes no files', async () => {
  const cap = await loadChatAttachments({ calls: { limits: async () => ({ data: { enabled: false, kinds: [], accept: [], max_files: 0, max_bytes: 0 } }), upload: async () => ({}) } });
  assert.equal(cap, undefined);
});

test('a stored message with files becomes attachment parts, and a file alone is not a hidden turn', () => {
  const row = storedMessageOf({ id: 'm', seq: 1, role: 'user', text: '', status: 'done', error_code: '', parts: [], created_at: '2026-01-01T00:00:00Z', attachments: [{ id: 'a', name: 'n.png', mime: 'image/png', size: 3, kind: 'image', url: 'u' }] });
  assert.deepEqual(fromStored(row, 'failed').parts.map((part) => part.type), ['attachment']);
});

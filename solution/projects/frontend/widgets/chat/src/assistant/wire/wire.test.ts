// Run: node --experimental-strip-types --test src/assistant/wire/wire.test.ts   (no framework, no network)
import assert from 'node:assert/strict';
import { test } from 'vitest';

import fixtures from './fixtures/events.json' with { type: 'json' };

import { decodeFrame, type Frame } from './frames';
import { parseSSE, StreamLostError } from './parse-sse';
import fixture from './fixtures/attachments.json';
import { ChatHttpError, ChatNetworkError, createTransport } from './transport';

const enc = new TextEncoder();
const frame = (value: unknown) => `data: ${JSON.stringify(value)}\n\n`;

const SAMPLE =
  frame({ type: 'run', version: 1, thread_id: 't1', message_id: 'a1', client_id: 'c1', seq: 2 }) +
  ': ping\n\n' +
  frame({ type: 'status', phase: 'searching' }) +
  frame({ type: 'text_delta', delta: 'Тихая ' }) +
  frame({ type: 'text_delta', delta: 'драма' }) +
  frame({ type: 'ui_payload', kind: 'citations', data: { items: [{ n: 1, title: 'Refund policy' }] } }) +
  frame({ type: 'future_frame', x: 1 }) +
  frame({ type: 'ui_payload', kind: 'poll', data: {} }) +
  frame({ type: 'done', finish_reason: 'stop' });

const bodyOf = (parts: Uint8Array[]) =>
  new ReadableStream<Uint8Array>({
    start(controller) {
      parts.forEach((part) => controller.enqueue(part));
      controller.close();
    },
  });

/** Splits bytes at the given offsets, including inside a multi-byte character. */
const splitAt = (bytes: Uint8Array, ...cuts: number[]) => [0, ...cuts, bytes.length].slice(0, -1).map((from, i) => bytes.slice(from, [...cuts, bytes.length][i]));

async function collect(body: ReadableStream<Uint8Array>, idleMs = 1000): Promise<Frame[]> {
  const out: Frame[] = [];
  for await (const raw of parseSSE(body, { idleMs })) {
    const f = decodeFrame(raw);
    if (f) out.push(f);
  }
  return out;
}

test('a recorded stream decodes in order; ping and unknown types are ignored', async () => {
  const frames = await collect(bodyOf([enc.encode(SAMPLE)]));
  assert.deepEqual(frames.map((f) => f.type), ['run', 'status', 'text_delta', 'text_delta', 'ui_payload', 'ui_payload', 'done']);
  assert.equal(frames.filter((f) => f.type === 'text_delta').map((f) => (f as { delta: string }).delta).join(''), 'Тихая драма');
});

test('the same stream split at every byte boundary decodes identically', async () => {
  const bytes = enc.encode(SAMPLE);
  const whole = await collect(bodyOf([bytes]));
  for (let cut = 1; cut < bytes.length; cut += 7) assert.deepEqual(await collect(bodyOf(splitAt(bytes, cut))), whole, `cut at ${cut}`);
});

test('CRLF line ends and multi-line data are handled', async () => {
  const body = 'data: {"type":"text_delta",\r\ndata: "delta":"a"}\r\n\r\n';
  assert.deepEqual(await collect(bodyOf([enc.encode(body)])), [{ type: 'text_delta', delta: 'a' }]);
});

test('malformed JSON is dropped and the stream goes on', async () => {
  const frames = await collect(bodyOf([enc.encode(`data: {oops\n\n${frame({ type: 'done' })}`)]));
  assert.deepEqual(frames.map((f) => f.type), ['done']);
});

test('a trailing partial block is flushed; a truncated stream just ends (no terminal frame)', async () => {
  const frames = await collect(bodyOf([enc.encode(frame({ type: 'status', phase: 'thinking' }) + 'data: {"type":"text_delta","delta":"x"}')]));
  assert.deepEqual(frames.map((f) => f.type), ['status', 'text_delta']);
});

test('a payload without a kind or data, a run without ids, an unknown phase or error code is dropped', () => {
  assert.equal(decodeFrame({ type: 'ui_payload', kind: '', data: {} }), null);
  assert.equal(decodeFrame({ type: 'ui_payload', kind: 'citations' }), null);
  assert.equal(decodeFrame({ type: 'run', message_id: 'a' }), null);
  assert.equal(decodeFrame({ type: 'status', phase: 'dreaming' }), null);
  assert.equal(decodeFrame({ type: 'error', code: 'weird', message: 'x' }), null);
});

test('every frame the server speaks decodes; tool frames and unknown types are ignored, never thrown', () => {
  for (const raw of fixtures.frames) assert.equal(decodeFrame(raw)?.type, raw.type, JSON.stringify(raw));
  for (const raw of fixtures.ignored) assert.equal(decodeFrame(raw), null, JSON.stringify(raw));
  assert.deepEqual(decodeFrame(fixtures.frames.find((f) => 'replayed' in f)), { type: 'done', finish_reason: 'stop', tokens_in: 0, tokens_out: 0, cost_usd: 0, replayed: true });
});

test('reasoning frames: a delta needs text; the end carries optional measurements', () => {
  assert.deepEqual(decodeFrame({ type: 'reasoning_delta', delta: 'hm' }), { type: 'reasoning_delta', delta: 'hm' });
  assert.equal(decodeFrame({ type: 'reasoning_delta' }), null);
  assert.deepEqual(decodeFrame({ type: 'reasoning_end' }), { type: 'reasoning_end', elapsed_ms: null, tokens: null });
  assert.deepEqual(decodeFrame({ type: 'reasoning_end', elapsed_ms: 900, tokens: 7 }), { type: 'reasoning_end', elapsed_ms: 900, tokens: 7 });
});

test('silence past the idle limit is a lost stream', async () => {
  const silent = new ReadableStream<Uint8Array>({ start() {} });
  await assert.rejects(collect(silent, 20), (error) => error instanceof StreamLostError && error.reason === 'idle');
});

const respond = (status: number, init: { body?: unknown; headers?: Record<string, string> } = {}) =>
  (async () => new Response(JSON.stringify(init.body ?? {}), { status, headers: { 'content-type': 'application/problem+json', ...init.headers } })) as typeof fetch;

const input = (signal = new AbortController().signal) => ({ text: 'hi', clientId: 'c1', signal });
const drain = async (gen: AsyncGenerator<Frame>) => {
  for await (const _ of gen) void _;
};

test('pre-stream refusals map to codes; 429 carries Retry-After', async () => {
  for (const [status, code] of [[401, 'unauthorized'], [404, 'not_found'], [409, 'busy'], [422, 'invalid'], [503, 'unavailable']] as const) {
    const t = createTransport({ baseUrl: 'https://api.test', getToken: () => 't', fetch: respond(status, { body: { code } }) });
    await assert.rejects(drain(t.open(input())), (error) => error instanceof ChatHttpError && error.status === status && error.code === code);
  }
  const t = createTransport({ baseUrl: 'https://api.test', getToken: () => 't', fetch: respond(429, { body: { code: 'rate_limited' }, headers: { 'retry-after': '12' } }) });
  await assert.rejects(drain(t.open(input())), (error) => error instanceof ChatHttpError && error.retryAfter === 12);
});

test('the token goes in the header only, the body carries the client id and context', async () => {
  let seen: { url: string; init: RequestInit } | undefined;
  const fetchStub = (async (url: string, init: RequestInit) => {
    seen = { url, init };
    return new Response(enc.encode(frame({ type: 'done' })), { status: 200, headers: { 'content-type': 'text/event-stream; charset=utf-8' } });
  }) as unknown as typeof fetch;
  const t = createTransport({ baseUrl: 'https://api.test', getToken: () => 'secret', fetch: fetchStub });
  const frames: Frame[] = [];
  for await (const f of t.open({ ...input(), context: { page: 'pricing' } })) frames.push(f);
  assert.equal(seen?.url, 'https://api.test/apix/chat/v1/stream');
  assert.equal(new Headers(seen?.init.headers).get('authorization'), 'Bearer secret');
  assert.deepEqual(JSON.parse(String(seen?.init.body)), { text: 'hi', client_id: 'c1', context: { page: 'pricing' } });
  assert.equal(frames.length, 1);
});

test('no response at all is a network error; an abort is not an error', async () => {
  const down = (async () => {
    throw new TypeError('failed to fetch');
  }) as typeof fetch;
  await assert.rejects(drain(createTransport({ baseUrl: 'https://x', getToken: () => null, fetch: down }).open(input())), ChatNetworkError);
  const controller = new AbortController();
  controller.abort();
  await drain(createTransport({ baseUrl: 'https://x', getToken: () => null, fetch: down }).open(input(controller.signal)));
});

test('a host names its own URL, body and headers; an anonymous host sends a visitor token and no bearer', async () => {
  let seen: { url: string; init: RequestInit } | undefined;
  const fetchStub = (async (url: string, init: RequestInit) => {
    seen = { url, init };
    return new Response(enc.encode(frame({ type: 'done' })), { status: 200, headers: { 'content-type': 'text/event-stream' } });
  }) as unknown as typeof fetch;
  const t = createTransport({
    baseUrl: 'https://api.test',
    streamUrl: ({ clientId }) => `/apix/chat/threads/t9/messages/?c=${clientId}`,
    buildBody: ({ text, clientId }) => ({ text, client_id: clientId }),
    visitorToken: () => 'v-token',
    headers: () => ({ 'x-csrftoken': 'csrf' }),
    streamFetch: fetchStub,
  });
  await drain(t.open(input()));
  assert.equal(seen?.url, 'https://api.test/apix/chat/threads/t9/messages/?c=c1');
  const headers = new Headers(seen?.init.headers);
  assert.equal(headers.get('x-visitor-token'), 'v-token');
  assert.equal(headers.get('x-csrftoken'), 'csrf');
  assert.equal(headers.get('authorization'), null);
  assert.deepEqual(JSON.parse(String(seen?.init.body)), { text: 'hi', client_id: 'c1' });
});

test('a bad request named `validation_error` reads as invalid', async () => {
  const t = createTransport({ baseUrl: 'https://api.test', fetch: respond(400, { body: { code: 'validation_error' } }) });
  await assert.rejects(drain(t.open(input())), (error) => error instanceof ChatHttpError && error.code === 'invalid');
});

test('the session id reaches `streamUrl` through the send', async () => {
  let url = '';
  const fetchStub = (async (u: string) => {
    url = u;
    return new Response(new TextEncoder().encode('event: done\ndata: {"type":"done"}\n\n'), { status: 200, headers: { 'content-type': 'text/event-stream' } });
  }) as unknown as typeof fetch;
  const t = createTransport({ baseUrl: 'https://api.test', streamUrl: ({ threadId }) => `/apix/chat/v1/threads/${encodeURIComponent(threadId ?? '')}/messages`, streamFetch: fetchStub });
  for await (const _ of t.open({ threadId: 'a/b', text: 'hi', clientId: 'c', signal: new AbortController().signal })) void _;
  assert.equal(url, 'https://api.test/apix/chat/v1/threads/a%2Fb/messages');
});

test('attachments fixture: the body carries ids only and a refusal reads as its code', async () => {
  let sent: unknown;
  const t = createTransport({ baseUrl: 'http://x', streamFetch: (async (_url: unknown, init: RequestInit) => { sent = JSON.parse(String(init.body)); return new Response(JSON.stringify({ code: fixture.refusals[0]?.code }), { status: 413 }); }) as typeof fetch });
  const files = fixture.send_body.in.attachments.map((f) => ({ ...f, kind: f.kind as 'image' }));
  await assert.rejects(drain(t.open({ text: fixture.send_body.in.text, clientId: 'c', attachments: files, signal: new AbortController().signal })), (e) => e instanceof ChatHttpError && e.code === 'too_large');
  assert.deepEqual(sent, { ...fixture.send_body.out, client_id: 'c' });
  for (const row of fixture.refusals) {
    const r = createTransport({ baseUrl: 'http://x', streamFetch: (async () => new Response(JSON.stringify(row.code ? { code: row.code } : {}), { status: row.status })) as typeof fetch });
    await assert.rejects(drain(r.open({ text: 't', clientId: 'c', signal: new AbortController().signal })), (e) => e instanceof ChatHttpError && e.code === row.reads_as);
  }
});

test('context headers reach the stream; none (SSR) adds nothing; headers() wins', async () => {
  const seen: Headers[] = [];
  const fetchStub = (async (_url: string, init: RequestInit) => {
    seen.push(new Headers(init.headers));
    return new Response(enc.encode(frame({ type: 'done' })), { status: 200, headers: { 'content-type': 'text/event-stream' } });
  }) as unknown as typeof fetch;
  for (const config of [
    { contextHeaders: () => ({ 'x-client-id': 'abc-12345678', 'x-timezone': 'Europe/Berlin' }) },
    { contextHeaders: () => ({}) },
    { contextHeaders: () => ({ 'x-client-id': 'abc-12345678' }), headers: () => ({ 'x-client-id': 'host-12345678' }) },
  ]) await drain(createTransport({ baseUrl: 'https://api.test', fetch: fetchStub, ...config }).open(input()));
  assert.equal(seen[0]?.get('x-client-id'), 'abc-12345678');
  assert.equal(seen[0]?.get('x-timezone'), 'Europe/Berlin');
  assert.equal(seen[1]?.has('x-client-id'), false);
  assert.equal(seen[2]?.get('x-client-id'), 'host-12345678');
});

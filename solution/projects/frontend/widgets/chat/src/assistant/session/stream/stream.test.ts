// Run: node --experimental-strip-types --test src/stream/stream.test.ts   (no framework, no network)
import assert from 'node:assert/strict';
import { test } from 'vitest';

import type { SendRequest, StreamChunk } from '../../../chat/core';

import type { Frame, Phase } from '../../wire/frames';
import { decodeStep } from '../../wire/trace';
import { StreamLostError } from '../../wire/parse-sse';
import type { StoredConversation, StoredMessage } from '../../wire/stored';
import { ChatHttpError, ChatNetworkError, type ChatTransport } from '../../wire/transport';
import { createStreamAdapter, sendFeedbackTurn } from './adapter';
import { fromStored, fromStoredThread } from './from-stored';
import { reconcile } from './reconcile';
import { payloadKindsOf } from './use-session';

/** A turn for the room (the chat's `SendRequest`): no recipient, no mentions. */
const request = (text: string, signal: AbortSignal): SendRequest => ({ text, history: [], recipient: 'all', mentions: [], messageId: 'u1', attachments: [], signal });

const RUN: Frame = { type: 'run', version: 1, thread_id: 't', message_id: 'a1', client_id: 'cid', seq: 2 };
const delta = (d: string): Frame => ({ type: 'text_delta', delta: d });
const cards: Frame = { type: 'ui_payload', kind: 'citations', data: { items: [{ n: 1, title: 'Refund policy' }] } };
const DONE: Frame = { type: 'done', finish_reason: 'stop', tokens_in: null, tokens_out: null, cost_usd: null, replayed: false };

const MESSAGES = {
  rejected: (e: ChatHttpError) => `rejected:${e.code}`,
  streamError: (code: string) => `error:${code}`,
  failed: 'failed',
};

function scripted(steps: Array<Frame | Error>, seen: { clientIds: string[] } = { clientIds: [] }): ChatTransport {
  return {
    async *open(input) {
      seen.clientIds.push(input.clientId);
      for (const step of steps) {
        if (step instanceof Error) throw step;
        yield step;
      }
    },
  };
}

async function run(transport: ChatTransport, options: { signal?: AbortSignal; statuses?: Array<Phase | null>; coalesceMs?: number } = {}) {
  const statuses = options.statuses ?? [];
  const adapter = createStreamAdapter({ transport, getContext: () => undefined, onStatus: (p) => statuses.push(p), messages: MESSAGES, newId: () => 'cid', coalesceMs: options.coalesceMs ?? 0 });
  const stream = await adapter.sendMessage(request('quiet', options.signal ?? new AbortController().signal));
  const chunks: StreamChunk[] = [];
  const reader = stream.getReader();
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
  }
  return chunks;
}

const types = (chunks: StreamChunk[]) => chunks.map((c) => c.type);

test('a full run: message, text, cards after the text, finish; status stays out of the transcript', async () => {
  const statuses: Array<Phase | null> = [];
  const chunks = await run(scripted([RUN, { type: 'status', phase: 'searching' }, delta('Here '), delta('you go.'), cards, delta(' Enjoy.'), DONE]), { statuses });
  assert.deepEqual(types(chunks), ['message-start', 'text-start', 'text-delta', 'text-delta', 'data', 'text-start', 'text-delta', 'finish']);
  assert.deepEqual(statuses, ['searching', null]);
  const data = chunks.find((c) => c.type === 'data');
  assert.deepEqual(data && data.type === 'data' ? [data.part.kind, data.part.data] : null, ['citations', { items: [{ n: 1, title: 'Refund policy' }] }]);
});

test('optional reasoning frames become a Reasoning part, sealed before the text; a host that sends none is unchanged', async () => {
  const think = (d: string): Frame => ({ type: 'reasoning_delta', delta: d });
  const chunks = await run(scripted([RUN, think('Look '), think('up.'), { type: 'reasoning_end', elapsed_ms: 800, tokens: 5 }, delta('Answer'), DONE]));
  assert.deepEqual(types(chunks), ['message-start', 'reasoning-start', 'reasoning-delta', 'reasoning-delta', 'reasoning-end', 'text-start', 'text-delta', 'finish']);
  const end = chunks.find((c) => c.type === 'reasoning-end');
  assert.deepEqual(end && end.type === 'reasoning-end' ? [end.elapsedMs, end.tokens] : null, [800, 5]);
  const joined = chunks.filter((c) => c.type === 'reasoning-delta').map((c) => (c as { delta: string }).delta).join('');
  assert.equal(joined, 'Look up.');
});

test('a thought with no reasoning_end is sealed by the next part, by done, by an error and by a lost stream', async () => {
  const think: Frame = { type: 'reasoning_delta', delta: 'x' };
  assert.deepEqual(types(await run(scripted([RUN, think, delta('a'), DONE]))), ['message-start', 'reasoning-start', 'reasoning-delta', 'reasoning-end', 'text-start', 'text-delta', 'finish']);
  assert.deepEqual(types(await run(scripted([RUN, think, cards, DONE]))), ['message-start', 'reasoning-start', 'reasoning-delta', 'reasoning-end', 'data', 'finish']);
  assert.deepEqual(types(await run(scripted([RUN, think, DONE]))), ['message-start', 'reasoning-start', 'reasoning-delta', 'reasoning-end', 'finish']);
  assert.deepEqual(types(await run(scripted([RUN, think, { type: 'error', code: 'failed', message: 'm', retryable: true }]))), ['message-start', 'reasoning-start', 'reasoning-delta', 'reasoning-end', 'error']);
  assert.deepEqual(types(await run(scripted([RUN, think, new StreamLostError('idle')]))), ['message-start', 'reasoning-start', 'reasoning-delta', 'reasoning-end', 'interrupted']);
});

test('a stray reasoning_end, or reasoning before run, is ignored; text then a second thought opens a second part', async () => {
  const think: Frame = { type: 'reasoning_delta', delta: 'x' };
  assert.deepEqual(types(await run(scripted([{ type: 'reasoning_end', elapsed_ms: 1, tokens: 1 }, think, RUN, DONE]))), ['message-start', 'finish']);
  assert.deepEqual(
    types(await run(scripted([RUN, delta('a'), think, delta('b'), DONE]), { coalesceMs: 50 })),
    ['message-start', 'text-start', 'text-delta', 'reasoning-start', 'reasoning-delta', 'reasoning-end', 'text-start', 'text-delta', 'finish'],
  );
});

test('deltas inside one coalescing window become one chunk', async () => {
  const chunks = await run(scripted([RUN, delta('a'), delta('b'), delta('c'), DONE]), { coalesceMs: 50 });
  const text = chunks.filter((c) => c.type === 'text-delta');
  assert.equal(text.length, 1);
  assert.equal(text[0]?.type === 'text-delta' && text[0].delta, 'abc');
});

test('an error frame keeps the partial text and ends with one error', async () => {
  const chunks = await run(scripted([RUN, delta('Half'), { type: 'error', code: 'timeout', message: 'slow', retryable: true }]));
  assert.deepEqual(types(chunks), ['message-start', 'text-start', 'text-delta', 'error']);
  assert.equal(chunks.at(-1)?.type === 'error' && chunks.at(-1)?.type === 'error' && (chunks.at(-1) as { message: string }).message, 'error:timeout');
});

test('a stream that ends without done or error is interrupted, not finished', async () => {
  assert.deepEqual(types(await run(scripted([RUN, delta('Cut')]))), ['message-start', 'text-start', 'text-delta', 'interrupted']);
  assert.deepEqual(types(await run(scripted([RUN, delta('Cut'), new StreamLostError('idle')]))), ['message-start', 'text-start', 'text-delta', 'interrupted']);
});

test('Stop (abort) keeps the partial text and says nothing more', async () => {
  const controller = new AbortController();
  const transport: ChatTransport = {
    async *open() {
      yield RUN;
      yield delta('Partial');
      controller.abort();
    },
  };
  const chunks = await run(transport, { signal: controller.signal });
  assert.deepEqual(types(chunks), ['message-start', 'text-start', 'text-delta']);
});

test('a refusal before any frame is one error message, reported to the host', async () => {
  const rejected: ChatHttpError[] = [];
  const adapter = createStreamAdapter({ transport: scripted([new ChatHttpError(429, 'rate_limited', 12)]), getContext: () => undefined, onStatus: () => undefined, onRejected: (e) => rejected.push(e), messages: MESSAGES, newId: () => 'cid', coalesceMs: 0 });
  const reader = (await adapter.sendMessage(request('x', new AbortController().signal))).getReader();
  const out: StreamChunk[] = [];
  for (let r = await reader.read(); !r.done; r = await reader.read()) out.push(r.value);
  assert.deepEqual(types(out), ['message-start', 'error']);
  assert.equal(rejected[0]?.retryAfter, 12);
});

test('a resend of a message that never reached `run` reuses its client id; after a run it does not', async () => {
  const seen = { clientIds: [] as string[] };
  let n = 0;
  const adapter = createStreamAdapter({ transport: scripted([new ChatNetworkError()], seen), getContext: () => undefined, onStatus: () => undefined, messages: MESSAGES, newId: () => `id${++n}`, coalesceMs: 0 });
  const send = async (text: string, transport?: ChatTransport) => {
    const a = transport ? createStreamAdapter({ transport, getContext: () => undefined, onStatus: () => undefined, messages: MESSAGES, newId: () => `id${++n}`, coalesceMs: 0 }) : adapter;
    const reader = (await a.sendMessage(request(text, new AbortController().signal))).getReader();
    while (!(await reader.read()).done);
  };
  await send('same');
  await send('same');
  assert.deepEqual(seen.clientIds, ['id1', 'id1']);
  await send('other');
  assert.equal(seen.clientIds[2], 'id2');
});

const stored = (over: Partial<StoredMessage>): StoredMessage => ({ id: 'm', seq: 1, role: 'assistant', text: '', parts: [], status: 'done', error_code: null, created_at: '2026-10-24T10:00:00Z', ...over });
const thread = (...messages: StoredMessage[]): StoredConversation => ({ id: 'c1', messages });

test('stored messages map to widget messages: text then payloads, whatever their kind; running and cancelled read as interrupted', () => {
  const done = fromStored(stored({ text: 'Hi', parts: [{ kind: 'citations', data: { items: [] } }, { kind: 'poll', data: {} }] }), 'failed');
  assert.deepEqual(done.parts.map((p) => p.type), ['text', 'data', 'data']);
  assert.equal(done.status.state, 'complete');
  assert.equal(fromStored(stored({ status: 'running' }), 'f').status.state, 'interrupted');
  assert.equal(fromStored(stored({ status: 'cancelled' }), 'f').status.state, 'interrupted');
  assert.deepEqual(fromStored(stored({ status: 'error' }), 'It failed').status, { state: 'failed', message: 'It failed' });
});

test('reconcile: final statuses return at once; running is polled then times out; no answer is lost', async () => {
  const signal = new AbortController().signal;
  const never = async () => undefined;
  assert.equal((await reconcile({ fetchConversation: async () => thread(stored({ status: 'done' })), signal })).outcome, 'done');
  assert.equal((await reconcile({ fetchConversation: async () => thread(stored({ status: 'cancelled' })), signal })).outcome, 'cancelled');
  assert.equal((await reconcile({ fetchConversation: async () => thread(stored({ role: 'user' })), signal })).outcome, 'lost');

  let calls = 0;
  let clock = 0;
  const outcome = await reconcile({
    fetchConversation: async () => thread(stored({ status: ++calls < 3 ? 'running' : 'done' })),
    signal,
    sleep: async (ms) => void (clock += ms),
    now: () => clock,
  });
  assert.equal(outcome.outcome, 'done');
  assert.equal(calls, 3);

  calls = 0;
  clock = 0;
  const stuck = await reconcile({ fetchConversation: async () => (calls++, thread(stored({ status: 'running' }))), signal, sleep: async (ms) => void (clock += ms), now: () => clock });
  assert.equal(stuck.outcome, 'timeout');
  assert.ok(calls <= 31);
  void never;
});

test('a live payload of a kind the host does not draw is dropped and reported; a known one is forwarded', async () => {
  const unknown: string[] = [];
  const adapter = createStreamAdapter({
    transport: scripted([RUN, delta('Hi'), { type: 'ui_payload', kind: 'poll', data: {} }, cards, DONE]),
    getContext: () => undefined,
    onStatus: () => undefined,
    payloadKinds: ['citations'],
    onUnknownPayload: (kind) => unknown.push(kind),
    messages: MESSAGES,
    newId: () => 'cid',
    coalesceMs: 0,
  });
  const reader = (await adapter.sendMessage(request('x', new AbortController().signal))).getReader();
  const out: StreamChunk[] = [];
  for (let r = await reader.read(); !r.done; r = await reader.read()) out.push(r.value);
  assert.deepEqual(unknown, ['poll']);
  assert.equal(out.filter((c) => c.type === 'data').length, 1);
});

test('a turn goes to the session `threadFor` names, and the host is told while it is in flight', async () => {
  const seen: Array<string | undefined> = [];
  const active: boolean[] = [];
  const transport: ChatTransport = {
    async *open(input) {
      seen.push(input.threadId);
      yield RUN;
      yield DONE;
    },
  };
  const adapter = createStreamAdapter({ transport, threadFor: async () => 's1', onActive: (a) => active.push(a), getContext: () => undefined, onStatus: () => undefined, messages: MESSAGES, newId: () => 'cid', coalesceMs: 0 });
  const reader = (await adapter.sendMessage(request('hi', new AbortController().signal))).getReader();
  while (!(await reader.read()).done);
  assert.deepEqual(seen, ['s1']);
  assert.deepEqual(active, [true, false]);
});

test('a session that cannot be created ends the turn as a failed message, and the host is told it is over', async () => {
  const active: boolean[] = [];
  const adapter = createStreamAdapter({ transport: scripted([RUN, DONE]), threadFor: async () => { throw new Error('create'); }, onActive: (a) => active.push(a), getContext: () => undefined, onStatus: () => undefined, messages: MESSAGES, newId: () => 'cid', coalesceMs: 0 });
  const reader = (await adapter.sendMessage(request('hi', new AbortController().signal))).getReader();
  const chunks: StreamChunk[] = [];
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
  }
  assert.equal(chunks.at(-1)?.type, 'error');
  assert.deepEqual(active, [true, false]);
});

test('sendFeedbackTurn posts empty text with context.feedback and adds no bubble; a refusal is thrown and reported', async () => {
  const seen: Array<{ text: string; context: unknown; threadId?: string }> = [];
  const transport: ChatTransport = {
    async *open(input) {
      seen.push({ text: input.text, context: input.context, threadId: input.threadId });
      yield RUN;
      yield delta('ok');
      yield DONE;
    },
  };
  const active: boolean[] = [];
  await sendFeedbackTurn({ transport, threadFor: async () => 'th1', getContext: () => ({ page: 'p' }), onStatus: () => undefined, onActive: (a) => active.push(a), newId: () => 'cid' }, 'm1', { applied: true }, new AbortController().signal);
  assert.deepEqual(seen, [{ text: '', context: { page: 'p', feedback: { message_id: 'm1', payload: { applied: true } } }, threadId: 'th1' }]);
  assert.deepEqual(active, [true, false]);

  const refused: ChatHttpError[] = [];
  const conflict = new ChatHttpError(409, 'already_given');
  const failing: ChatTransport = { async *open() { yield* []; throw conflict; } };
  await assert.rejects(
    sendFeedbackTurn({ transport: failing, getContext: () => undefined, onStatus: () => undefined, onRejected: (e) => refused.push(e) }, 'm1', {}, new AbortController().signal),
    (error) => error === conflict,
  );
  assert.deepEqual(refused, [conflict]);
});

test('a hidden feedback row (user, no text, no parts) is left out of a reloaded transcript', () => {
  const row = (id: string, role: 'user' | 'assistant', text: string): StoredMessage => ({ id, seq: 1, role, text, parts: [], status: 'done', error_code: null, created_at: '2026-11-08T10:00:00Z' });
  const shown = fromStoredThread([row('u1', 'user', 'hi'), row('a1', 'assistant', 'hello'), row('u2', 'user', ''), row('a2', 'assistant', 'thanks')], 'failed');
  assert.deepEqual(shown.map((m) => m.id), ['u1', 'a1', 'a2']);
});

const step = (stepId: string, status: string, over: Record<string, unknown> = {}): Frame => {
  const decoded = decodeStep({ v: 1, step_id: stepId, seq: Number(stepId.slice(1)), kind: 'tool', status, name: 'kb_search', redaction: 'none', ...over });
  if (!decoded) throw new Error('bad step');
  return { type: 'trace_step', event_seq: null, step: decoded };
};

test('a trace step is a step chunk; the same step sent again updates it; a new step ends the open text', async () => {
  const chunks = await run(scripted([RUN, delta('Looking. '), step('s1', 'running'), step('s1', 'ok'), delta('Found it.'), DONE]));
  assert.deepEqual(types(chunks), ['message-start', 'text-start', 'text-delta', 'step', 'step', 'text-start', 'text-delta', 'finish']);
  const ids = chunks.flatMap((c) => (c.type === 'step' ? [c.part.id] : []));
  assert.deepEqual(ids, ['a1:s1', 'a1:s1']);
});

test('a second step with a new id after the first settled does not reopen the first text part', async () => {
  const chunks = await run(scripted([RUN, step('s1', 'ok'), step('s2', 'ok'), DONE]));
  assert.deepEqual(types(chunks), ['message-start', 'step', 'step', 'finish']);
});

test('a thought is sealed before a step that follows it', async () => {
  const chunks = await run(scripted([RUN, { type: 'reasoning_delta', delta: 'hm' }, step('s1', 'running'), DONE]));
  assert.deepEqual(types(chunks), ['message-start', 'reasoning-start', 'reasoning-delta', 'reasoning-end', 'step', 'finish']);
});

test('a stored message restores what the answer did before its words; a null trace restores nothing', () => {
  const trace = { v: 1, steps_count: 2, steps: [{ v: 1, step_id: 's2', seq: 2, kind: 'tool', status: 'ok', name: 'b', redaction: 'none' }, { v: 1, step_id: 's1', seq: 1, kind: 'tool', status: 'ok', name: 'a', redaction: 'none' }] };
  const message = fromStored(stored({ id: 'a9', text: 'Done.', trace }), 'failed');
  assert.deepEqual(message.parts.map((p) => p.id), ['a9:s1', 'a9:s2', 'a9:t']);
  assert.deepEqual(fromStored(stored({ id: 'a9', text: 'Done.', trace: null }), 'failed').parts.map((p) => p.id), ['a9:t']);
});

test('payload kinds come from the renderers when the host gives no list: its keys and the package blocks; an explicit list wins; neither means no filter', () => {
  assert.equal(payloadKindsOf({}), undefined);
  assert.deepEqual(payloadKindsOf({ dataRenderers: { citations: () => null } }), ['citations', 'ask', 'approval', 'changes']);
  assert.deepEqual(payloadKindsOf({ payloadKinds: ['poll'], dataRenderers: { citations: () => null } }), ['poll']);
});

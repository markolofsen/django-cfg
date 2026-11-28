import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { createMockServer } from '../testing';
import { createRealtimeClient } from './realtime-client';

import type { MockServer, MockServerOptions } from '../testing';
import type { RealtimeClient, RealtimeClientOptions } from './realtime-client';

const flush = () => vi.advanceTimersByTimeAsync(0);
const wait = (ms: number) => vi.advanceTimersByTimeAsync(ms);

interface Harness {
  server: MockServer;
  client: RealtimeClient;
  wake: () => void;
  phase: () => string;
  sent: (op: string) => Record<string, unknown>[];
}

function setup(
  serverOptions: MockServerOptions = {},
  clientOptions: Partial<RealtimeClientOptions> = {},
): Harness {
  const server = createMockServer({ ping: 0, ...serverOptions });
  let onWake: () => void = () => {};
  const client = createRealtimeClient({
    url: server.url,
    WebSocket: server.WebSocket,
    random: () => 0.5,
    gapJitterMs: 0,
    wake: (fn) => {
      onWake = fn;
      return () => {
        onWake = () => {};
      };
    },
    onHandlerError: (error) => {
      throw error;
    },
    ...clientOptions,
  });
  return {
    server,
    client,
    wake: () => onWake(),
    phase: () => client.store.getSnapshot().connection.phase,
    sent: (op) => server.received.filter((r) => r.frame.op === op).map((r) => r.frame),
  };
}

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});

describe('lazy connection', () => {
  it('opens no socket until the first subscription', async () => {
    const h = setup();
    await wait(60_000);
    expect(h.server.connections).toBe(0);
    expect(h.phase()).toBe('idle');
  });

  it('connects on subscribe, subscribes after hello and delivers messages', async () => {
    const h = setup();
    const events: unknown[] = [];
    h.client.subscribe('demo.ping', (data, meta) => events.push([data, meta.offset]));
    expect(h.phase()).toBe('connecting');
    await flush();
    expect(h.phase()).toBe('live');
    expect(h.sent('sub')).toEqual([{ op: 'sub', id: 1, topic: 'demo.ping' }]);
    expect(h.client.store.getSnapshot().topics['demo.ping']?.status).toBe('live');

    h.server.publish('demo.ping', { n: 1 });
    await flush();
    expect(events).toEqual([[{ n: 1 }, '1:1']]);
    expect(h.client.store.getSnapshot().topics['demo.ping']?.offset).toBe('1:1');
  });

  it('closes the socket 30 s after the last topic leaves', async () => {
    const h = setup();
    const release = h.client.subscribe('demo.ping', () => {});
    await flush();
    release();
    await wait(1_500);
    expect(h.sent('unsub')).toEqual([{ op: 'unsub', topic: 'demo.ping' }]);
    expect(h.server.connections).toBe(1);
    await wait(29_999);
    expect(h.server.connections).toBe(1);
    await wait(1);
    expect(h.server.connections).toBe(0);
    expect(h.phase()).toBe('idle');
  });

  it('throws on a topic name the protocol cannot carry', () => {
    const h = setup();
    expect(() => h.client.subscribe('Orders 42', () => {})).toThrow(/invalid topic/);
  });
});

describe('reference counts', () => {
  it('shares one wire subscription and unsubscribes only after the last release plus 1.5 s', async () => {
    const h = setup();
    const a = h.client.subscribe('orders:42', () => {});
    const b = h.client.subscribe('orders:42', () => {});
    await flush();
    expect(h.sent('sub')).toHaveLength(1);
    expect(h.client.store.getSnapshot().topics['orders:42']?.subscribers).toBe(2);

    a();
    a();
    await wait(5_000);
    expect(h.sent('unsub')).toHaveLength(0);

    b();
    expect(h.client.store.getSnapshot().topics['orders:42']?.status).toBe('leaving');
    await wait(1_499);
    expect(h.sent('unsub')).toHaveLength(0);
    await wait(1);
    expect(h.sent('unsub')).toHaveLength(1);
    expect(h.client.store.getSnapshot().topics['orders:42']).toBeUndefined();
  });

  it('absorbs a StrictMode mount, unmount, mount with no extra frames', async () => {
    const h = setup();
    h.client.subscribe('orders:42', () => {})();
    h.client.subscribe('orders:42', () => {});
    await flush();
    await wait(10_000);
    expect(h.sent('sub')).toHaveLength(1);
    expect(h.sent('unsub')).toHaveLength(0);
    expect(h.client.store.getSnapshot().topics['orders:42']?.status).toBe('live');
  });

  it('delivers an event to a handler another handler removed during the same dispatch', async () => {
    const h = setup();
    const calls: string[] = [];
    let releaseB: () => void = () => {};
    h.client.subscribe('demo.ping', () => {
      calls.push('a');
      releaseB();
    });
    releaseB = h.client.subscribe('demo.ping', () => calls.push('b'));
    await flush();
    h.server.publish('demo.ping', 1);
    await flush();
    h.server.publish('demo.ping', 2);
    await flush();
    expect(calls).toEqual(['a', 'b', 'a']);
  });
});

describe('reconnect and replay', () => {
  it('resubscribes with since and receives what was published while down', async () => {
    const h = setup();
    const offsets: string[] = [];
    h.client.subscribe('orders:42', (_d, meta) => offsets.push(meta.offset));
    await flush();
    h.server.publish('orders:42', 'a');
    await flush();

    h.server.drop();
    await flush();
    expect(h.phase()).toBe('reconnecting');
    h.server.publish('orders:42', 'b');
    h.server.publish('orders:42', 'c');

    await wait(500);
    expect(h.phase()).toBe('live');
    expect(h.sent('sub').at(-1)).toEqual({ op: 'sub', id: 2, topic: 'orders:42', since: '1:1' });
    expect(offsets).toEqual(['1:1', '1:2', '1:3']);
  });

  it('keeps the sub_ok head as since when no message arrived', async () => {
    const h = setup();
    h.server.publish('orders:42', 'before');
    h.client.subscribe('orders:42', () => {});
    await flush();
    h.server.drop();
    await wait(500);
    expect(h.sent('sub').at(-1)?.since).toBe('1:1');
  });

  it('subscribes topics added while down once the socket is live', async () => {
    const h = setup();
    h.client.subscribe('demo.ping', () => {});
    await flush();
    h.server.drop();
    await flush();
    h.client.subscribe('orders:7', () => {});
    expect(h.client.store.getSnapshot().topics['orders:7']?.status).toBe('pending');
    await wait(500);
    expect(h.client.store.getSnapshot().topics['orders:7']?.status).toBe('live');
  });

  it('retries now on wake instead of waiting out the backoff', async () => {
    const h = setup({}, { random: () => 1 });
    h.client.subscribe('demo.ping', () => {});
    await flush();
    h.server.refuse(1006);
    h.server.drop();
    await wait(1_000 + 2_000 + 4_000);
    expect(h.client.store.getSnapshot().connection.attempt).toBe(4);
    h.server.refuse(null);
    expect(h.phase()).toBe('reconnecting');
    h.wake();
    await flush();
    expect(h.phase()).toBe('live');
  });

  it('treats no pong within 10 s of a ping as a dead socket', async () => {
    const h = setup({ ping: 10 });
    h.client.subscribe('demo.ping', () => {});
    await flush();
    await wait(25_000);
    expect(h.sent('ping')).toHaveLength(2);
    expect(h.phase()).toBe('live');

    h.server.answerPings(false);
    await wait(14_999);
    expect(h.phase()).toBe('live');
    await wait(1);
    expect(h.phase()).toBe('reconnecting');
    expect(h.client.store.getSnapshot().connection.lastClose?.reason).toBe('pong timeout');
    h.server.answerPings(true);
    await wait(500);
    expect(h.phase()).toBe('live');
  });
});

describe('gaps', () => {
  it('calls onGap once when history no longer reaches since', async () => {
    const h = setup();
    const onGap = vi.fn();
    const onEvent = vi.fn();
    h.client.subscribe('orders:42', { onEvent, onGap });
    await flush();
    h.server.publish('orders:42', 'a');
    await flush();
    h.server.drop();
    for (const v of ['b', 'c', 'd']) h.server.publish('orders:42', v);
    h.server.trim('orders:42', 1);

    await wait(500);
    await wait(1); // the refetch timer is armed by sub_ok, after the reconnect
    expect(onGap).toHaveBeenCalledTimes(1);
    expect(onGap).toHaveBeenCalledWith('orders:42');
    const topic = h.client.store.getSnapshot().topics['orders:42'];
    expect(topic?.offset).toBe('1:4');
    expect(topic?.gaps).toBe(1);
  });

  it('calls onGap when the topic started a new epoch', async () => {
    const h = setup();
    const onGap = vi.fn();
    h.client.subscribe('orders:42', { onEvent: () => {}, onGap });
    await flush();
    h.server.publish('orders:42', 'a');
    await flush();
    h.server.drop();
    h.server.bumpEpoch('orders:42');
    await wait(500);
    await wait(1);
    expect(onGap).toHaveBeenCalledTimes(1);
  });

  it('treats a repeated sub_ok{recovered:false} on a live subscription as a gap and adopts its offset', async () => {
    const h = setup();
    const onGap = vi.fn();
    const offsets: string[] = [];
    h.client.subscribe('orders:42', { onEvent: (_d, meta) => offsets.push(meta.offset), onGap });
    await flush();
    h.server.publish('orders:42', 'a');
    await flush();

    h.server.bumpEpoch('orders:42');
    await wait(1);
    expect(h.phase()).toBe('live');
    expect(onGap).toHaveBeenCalledTimes(1);
    const head = h.server.head('orders:42');
    expect(head).not.toMatch(/^1:/);
    expect(h.client.store.getSnapshot().topics['orders:42']?.offset).toBe(head);

    const next = h.server.publish('orders:42', 'b');
    await flush();
    expect(offsets).toEqual(['1:1', next]);

    h.server.bumpEpoch('orders:42');
    await wait(1);
    expect(onGap).toHaveBeenCalledTimes(2);

    h.server.drop();
    await wait(500);
    expect(h.sent('sub').at(-1)?.since).toBe(h.server.head('orders:42'));
  });

  it('never refetches because a reconnect landed on a restarted server', async () => {
    const h = setup();
    const onGap = vi.fn();
    h.client.subscribe('orders:42', { onEvent: () => {}, onGap });
    await flush();
    h.server.publish('orders:42', 'a');
    await flush();
    h.server.restart();
    await wait(5_000);
    expect(h.phase()).toBe('live');
    expect(h.sent('sub').at(-1)).toEqual({ op: 'sub', id: 2, topic: 'orders:42', since: '1:1' });
    expect(onGap).not.toHaveBeenCalled();
  });

  it('jitters the refetch over 0 to 2 s', async () => {
    const h = setup({}, { random: () => 0.5, gapJitterMs: 2_000 });
    const onGap = vi.fn();
    h.client.subscribe('orders:42', { onEvent: () => {}, onGap });
    await flush();
    h.server.publish('orders:42', 'a');
    await flush();
    h.server.drop();
    h.server.bumpEpoch('orders:42');
    await wait(1_000);
    expect(h.client.store.getSnapshot().topics['orders:42']?.gaps).toBe(1);
    expect(onGap).not.toHaveBeenCalled();
    await wait(1_000);
    expect(onGap).toHaveBeenCalledTimes(1);
  });

  it('does not report a gap for a recovered replay', async () => {
    const h = setup();
    const onGap = vi.fn();
    h.client.subscribe('orders:42', { onEvent: () => {}, onGap });
    await flush();
    h.server.drop();
    await wait(500);
    expect(onGap).not.toHaveBeenCalled();
  });
});

describe('close codes', () => {
  it.each([4401, 4403])('stops on %i until the auth state changes', async (code) => {
    const h = setup();
    h.client.subscribe('demo.ping', () => {});
    await flush();
    h.server.closeAll(code);
    await flush();
    expect(h.phase()).toBe('stopped');
    await wait(120_000);
    h.wake();
    await flush();
    expect(h.phase()).toBe('stopped');
    expect(h.server.connections).toBe(0);

    h.client.authChanged();
    await flush();
    expect(h.phase()).toBe('live');
  });

  it('reconnects and replays after 1013 (slow consumer)', async () => {
    const h = setup();
    const offsets: string[] = [];
    h.client.subscribe('orders:42', (_d, meta) => offsets.push(meta.offset));
    await flush();
    h.server.publish('orders:42', 'a');
    await flush();
    h.server.closeAll(1013, 'slow consumer');
    h.server.publish('orders:42', 'b');
    await wait(2_500);
    expect(h.phase()).toBe('live');
    expect(offsets).toEqual(['1:1', '1:2']);
  });

  it('reconnects with backoff on 4408 and 4500', async () => {
    const h = setup();
    h.client.subscribe('demo.ping', () => {});
    await flush();
    for (const code of [4408, 4500]) {
      h.server.closeAll(code);
      await flush();
      expect(h.phase()).toBe('reconnecting');
      await wait(500);
      expect(h.phase()).toBe('live');
      await wait(10_000); // live long enough that the next drop is a first retry again
    }
  });

  it('spreads the first retry after 1012 over 0 to 5 s', async () => {
    const h = setup({}, { random: () => 0.8 });
    h.client.subscribe('demo.ping', () => {});
    await flush();
    h.server.restart();
    await flush();
    expect(h.client.store.getSnapshot().connection.retryAt).toBe(Date.now() + 4_000);
    await wait(4_000);
    expect(h.phase()).toBe('live');
  });

  it('refreshes credentials on 4419 and reconnects at once', async () => {
    const refreshCredentials = vi.fn(async () => true);
    const h = setup({}, { refreshCredentials });
    h.client.subscribe('demo.ping', () => {});
    await flush();
    h.server.closeAll(4419);
    await flush();
    expect(refreshCredentials).toHaveBeenCalledTimes(1);
    expect(h.phase()).toBe('live');
  });

  it('stays stopped on 4419 when no session is left', async () => {
    const h = setup({}, { refreshCredentials: async () => false });
    h.client.subscribe('demo.ping', () => {});
    await flush();
    h.server.closeAll(4419);
    await wait(60_000);
    expect(h.phase()).toBe('stopped');
  });

  it('retries 4429 with a 30 s floor instead of stopping', async () => {
    const h = setup();
    h.client.subscribe('demo.ping', () => {});
    await flush();
    h.server.closeAll(4429);
    await flush();
    expect(h.phase()).toBe('reconnecting');
    await wait(30_499);
    expect(h.phase()).toBe('reconnecting');
    await wait(1);
    expect(h.phase()).toBe('live');
  });

  it('resets the attempt counter only after 10 s live', async () => {
    const h = setup();
    h.client.subscribe('demo.ping', () => {});
    await flush();
    const attempts: number[] = [];
    for (let i = 0; i < 3; i += 1) {
      h.server.drop();
      await flush();
      attempts.push(h.client.store.getSnapshot().connection.attempt);
      await wait(20_000);
      expect(h.phase()).toBe('live');
      await wait(0);
    }
    expect(attempts).toEqual([1, 1, 1]);

    const quick: number[] = [];
    for (let i = 0; i < 3; i += 1) {
      await wait(1);
      h.server.drop();
      await flush();
      quick.push(h.client.store.getSnapshot().connection.attempt);
      await wait(quick.length * 2_000);
    }
    expect(quick).toEqual([1, 2, 3]);
  });

  it('resume() retries only a stopped connection', async () => {
    const h = setup();
    h.client.subscribe('demo.ping', () => {});
    await flush();
    h.client.resume();
    await flush();
    expect(h.server.received.filter((r) => r.frame.op === 'sub')).toHaveLength(1);

    h.server.closeAll(4401);
    await flush();
    h.client.resume();
    await flush();
    expect(h.phase()).toBe('live');
  });
});

describe('auth', () => {
  it('sends the token as the first frame and redacts it in the frame log', async () => {
    const h = setup({ authenticate: () => 7 }, { getToken: () => 'secret-token' });
    h.client.store.retainFrames();
    h.client.subscribe('demo.ping', () => {});
    await flush();
    expect(h.server.received[0]?.frame).toEqual({ op: 'auth', token: 'secret-token' });
    expect(h.client.store.getSnapshot().connection.user).toBe(7);
    const texts = h.client.store.getSnapshot().frames.map((f) => f.text).join('\n');
    expect(texts).not.toContain('secret-token');
    expect(texts).toContain('[redacted]');
  });

  it('reconnects an open socket on authChanged and keeps the offsets', async () => {
    let token: string | null = null;
    const h = setup({}, { getToken: () => token });
    h.client.subscribe('orders:42', () => {});
    await flush();
    h.server.publish('orders:42', 'a');
    await flush();
    expect(h.client.store.getSnapshot().connection.user).toBeNull();

    token = '7';
    h.client.authChanged();
    await flush();
    expect(h.client.store.getSnapshot().connection.user).toBe('7');
    expect(h.sent('sub').at(-1)).toEqual({ op: 'sub', id: 2, topic: 'orders:42', since: '1:1' });
  });

  it('does not retry a refused topic until the auth state changes', async () => {
    const h = setup({ authorize: (_topic, user) => (user === null ? 'forbidden' : null) });
    let token: string | null = null;
    const onRefused = vi.fn();
    const client = createRealtimeClient({
      url: h.server.url,
      WebSocket: h.server.WebSocket,
      random: () => 0,
      wake: () => () => {},
      getToken: () => token,
    });
    client.subscribe('orders:42', { onEvent: () => {}, onRefused });
    await flush();
    expect(onRefused).toHaveBeenCalledWith('forbidden', 'orders:42');
    expect(client.store.getSnapshot().topics['orders:42']?.status).toBe('refused');

    h.server.drop();
    await wait(500);
    expect(h.sent('sub')).toHaveLength(1);

    token = '7';
    client.authChanged();
    await flush();
    expect(h.sent('sub')).toHaveLength(2);
    expect(client.store.getSnapshot().topics['orders:42']?.status).toBe('live');
  });
});

describe('sub_err timeout', () => {
  it('retries a timed-out subscription with backoff', async () => {
    let refusals = 2;
    const h = setup({ authorize: () => (refusals-- > 0 ? 'timeout' : null) });
    h.client.subscribe('orders:42', () => {});
    await flush();
    expect(h.client.store.getSnapshot().topics['orders:42']?.status).toBe('pending');
    await wait(500);
    expect(h.sent('sub')).toHaveLength(2);
    await wait(999);
    expect(h.sent('sub')).toHaveLength(2); // the second timeout backs off further
    await wait(1);
    expect(h.sent('sub')).toHaveLength(3);
    expect(h.client.store.getSnapshot().topics['orders:42']?.status).toBe('live');
  });
});

describe('connection id', () => {
  it('exposes the cid and passes origin_cid to handlers; the sender does not get its own echo', async () => {
    const h = setup();
    const metas: unknown[] = [];
    h.client.subscribe('orders:42', (_d, meta) => metas.push(meta.originCid));
    await flush();
    const cid = h.client.getCid();
    expect(cid).toBe(h.server.cids[0]);
    h.server.publish('orders:42', 'mine', { originCid: cid ?? '' });
    h.server.publish('orders:42', 'theirs', { originCid: 'c99' });
    await flush();
    expect(metas).toEqual(['c99']);
    h.server.drop();
    await flush();
    expect(h.client.getCid()).toBeNull();
  });
});

describe('without a WebSocket', () => {
  it('stops with a reason instead of throwing', async () => {
    const client = createRealtimeClient({ url: 'ws://x/ws', wake: () => () => {}, random: () => 0 });
    const original = globalThis.WebSocket;
    vi.stubGlobal('WebSocket', undefined);
    client.subscribe('demo.ping', () => {});
    await flush();
    expect(client.store.getSnapshot().connection.phase).toBe('stopped');
    vi.stubGlobal('WebSocket', original);
    vi.unstubAllGlobals();
  });
});

describe('a gap with the revealing message', () => {
  it('delivers the msg that follows a sub_ok recovered:false with the same offset', async () => {
    const h = setup();
    const offsets: string[] = [];
    const onGap = vi.fn();
    h.client.subscribe('orders:42', { onEvent: (_d, meta) => offsets.push(meta.offset), onGap });
    await flush();
    h.server.sendRaw(JSON.stringify({ op: 'sub_ok', id: 1, topic: 'orders:42', offset: '9:1', recovered: false }));
    h.server.sendRaw(JSON.stringify({ op: 'msg', topic: 'orders:42', offset: '9:1', data: 'new epoch' }));
    h.server.sendRaw(JSON.stringify({ op: 'msg', topic: 'orders:42', offset: '9:1', data: 'duplicate' }));
    await wait(1);
    expect(offsets).toEqual(['9:1']);
    expect(onGap).toHaveBeenCalledTimes(1);
  });
});

describe('issues', () => {
  function withIssues(serverOptions: MockServerOptions = {}, clientOptions: Partial<RealtimeClientOptions> = {}) {
    const issues: unknown[] = [];
    const h = setup(serverOptions, { onIssue: (issue) => issues.push(issue), ...clientOptions });
    return { ...h, issues };
  }

  it('reports terminal closes and 4500 with the connection id', async () => {
    const h = withIssues();
    h.client.subscribe('demo.ping', () => {});
    await flush();
    h.server.closeAll(4500, 'boom');
    await wait(1_000);
    h.server.closeAll(4403, 'origin');
    await flush();
    expect(h.issues).toEqual([
      { kind: 'closed', code: 4500, reason: 'boom', cid: 'c1' },
      { kind: 'closed', code: 4403, reason: 'origin', cid: 'c2' },
    ]);
  });

  it('stays quiet on normal drops and on a 4419 refresh', async () => {
    const h = withIssues({}, { refreshCredentials: async () => true });
    h.client.subscribe('demo.ping', () => {});
    await flush();
    for (const code of [1006, 1011, 1012, 1013, 4408, 4419]) {
      h.server.closeAll(code);
      // Past the 10 s stable mark, so each drop is a first retry again.
      await wait(20_000);
      expect(h.phase()).toBe('live');
    }
    expect(h.issues).toEqual([]);
  });

  it('reports a run of failed handshakes once per streak', async () => {
    const h = withIssues();
    h.client.subscribe('demo.ping', () => {});
    await flush();
    h.server.refuse(1006);
    h.server.drop();
    await wait(120_000);
    expect(h.client.store.getSnapshot().connection.attempt).toBeGreaterThan(6);
    expect(h.issues).toEqual([{ kind: 'unreachable', attempts: 5, lastCode: 1006, lastReason: 'refused by mock server', cid: null }]);
  });

  it('reports forbidden, invalid and unknown topics, but not a timeout', async () => {
    const codes = ['forbidden', 'unknown_topic', 'timeout'] as const;
    const h = withIssues({ authorize: (topic) => codes[Number(topic.split(':')[1])] ?? null });
    h.client.subscribe('t:0', () => {});
    h.client.subscribe('t:1', () => {});
    h.client.subscribe('t:2', () => {});
    await flush();
    expect(h.issues).toEqual([
      { kind: 'refused', topic: 't:0', code: 'forbidden', cid: 'c1' },
      { kind: 'refused', topic: 't:1', code: 'unknown_topic', cid: 'c1' },
    ]);
  });

  it('reports protocol error frames and unparseable frames', async () => {
    const h = withIssues();
    h.client.subscribe('demo.ping', () => {});
    await flush();
    h.server.sendRaw(JSON.stringify({ op: 'error', code: 'rate', detail: 'too many frames' }));
    h.server.sendRaw('{"op":"presence"}');
    await flush();
    expect(h.issues).toEqual([
      { kind: 'protocol', code: 'rate', detail: 'too many frames', cid: 'c1' },
      { kind: 'protocol', code: 'unparseable', detail: 'unknown op "presence"', cid: 'c1' },
    ]);
  });
});

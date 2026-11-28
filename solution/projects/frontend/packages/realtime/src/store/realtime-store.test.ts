import { describe, expect, it, vi } from 'vitest';

import { createRealtimeStore } from './realtime-store';

describe('createRealtimeStore', () => {
  it('keeps slice identity across unrelated changes and skips no-op patches', () => {
    const store = createRealtimeStore();
    store.retainFrames();
    const listener = vi.fn();
    store.subscribe(listener);
    const connection = store.getSnapshot().connection;

    store.setConnection({ phase: 'idle' });
    expect(listener).not.toHaveBeenCalled();

    store.recordFrame({ at: 0, direction: 'in', op: 'pong', topic: null, text: '{"op":"pong"}' });
    expect(store.getSnapshot().connection).toBe(connection);
    expect(listener).toHaveBeenCalledTimes(1);

    store.setConnection({ phase: 'live' });
    expect(store.getSnapshot().connection).not.toBe(connection);
  });

  it('keeps only the last frames', () => {
    const store = createRealtimeStore(3);
    store.retainFrames();
    for (let i = 0; i < 5; i += 1) {
      store.recordFrame({ at: i, direction: 'out', op: 'ping', topic: null, text: String(i) });
    }
    expect(store.getSnapshot().frames.map((f) => f.text)).toEqual(['2', '3', '4']);
  });

  it('keeps no frames while nothing reads them', () => {
    const store = createRealtimeStore();
    store.recordFrame({ at: 0, direction: 'out', op: 'ping', topic: null, text: '' });
    expect(store.getSnapshot().frames).toHaveLength(0);
    const release = store.retainFrames();
    store.recordFrame({ at: 0, direction: 'out', op: 'ping', topic: null, text: '' });
    release();
    release();
    store.recordFrame({ at: 0, direction: 'out', op: 'ping', topic: null, text: '' });
    expect(store.getSnapshot().frames).toHaveLength(1);
    expect(store.recordingFrames).toBe(false);
  });

  it('removes a topic', () => {
    const store = createRealtimeStore();
    const state = { status: 'live' as const, offset: '1-0', subscribers: 1, refusal: null, received: 0, gaps: 0 };
    store.setTopic('orders:42', state);
    store.setTopic('orders:42', null);
    expect(store.getSnapshot().topics).toEqual({});
  });
});

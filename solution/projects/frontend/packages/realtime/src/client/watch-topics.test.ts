import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { createMockServer } from '../testing';
import { createRealtimeClient } from './realtime-client';
import { watchTopics } from './watch-topics';

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});

function setup() {
  const server = createMockServer({ ping: 0 });
  const client = createRealtimeClient({
    url: server.url,
    WebSocket: server.WebSocket,
    random: () => 0,
    wake: () => () => {},
  });
  return { server, client };
}

describe('watchTopics', () => {
  it('refreshes once when a fresh subscription goes live, so a publish before sub_ok is not lost', async () => {
    const { server, client } = setup();
    const onChange = vi.fn();
    watchTopics(client, ['orders:42', 'orders:list'], onChange);
    await vi.advanceTimersByTimeAsync(300);
    expect(onChange).toHaveBeenCalledTimes(1);

    // A second watcher joining the live topic missed everything before it: it refreshes too.
    const second = vi.fn();
    watchTopics(client, ['orders:42'], second);
    await vi.advanceTimersByTimeAsync(300);
    expect(second).toHaveBeenCalledTimes(1);

    // A resubscribe with `since` replays instead: no refresh.
    server.drop();
    await vi.advanceTimersByTimeAsync(5_000);
    expect(onChange).toHaveBeenCalledTimes(1);
    expect(second).toHaveBeenCalledTimes(1);
  });

  it('coalesces a burst of events on several topics into one change per window', async () => {
    const { server, client } = setup();
    const onChange = vi.fn();
    watchTopics(client, ['orders:42', 'orders:list'], onChange);
    await vi.advanceTimersByTimeAsync(300);
    onChange.mockClear();

    for (let i = 0; i < 5; i += 1) server.publish('orders:42', i);
    server.publish('orders:list', 'x');
    await vi.advanceTimersByTimeAsync(249);
    expect(onChange).not.toHaveBeenCalled();
    await vi.advanceTimersByTimeAsync(1);
    expect(onChange).toHaveBeenCalledTimes(1);

    server.publish('orders:42', 'later');
    await vi.advanceTimersByTimeAsync(250);
    expect(onChange).toHaveBeenCalledTimes(2);
  });

  it('counts a gap as a change', async () => {
    const { server, client } = setup();
    const onChange = vi.fn();
    watchTopics(client, ['orders:42'], onChange);
    await vi.advanceTimersByTimeAsync(300);
    onChange.mockClear();
    server.bumpEpoch('orders:42');
    await vi.advanceTimersByTimeAsync(251);
    expect(onChange).toHaveBeenCalledTimes(1);
  });

  it('releases its subscriptions and drops a pending change on detach', async () => {
    const { server, client } = setup();
    const onChange = vi.fn();
    const detach = watchTopics(client, ['orders:42'], onChange);
    await vi.advanceTimersByTimeAsync(0);
    server.publish('orders:42', 1);
    await vi.advanceTimersByTimeAsync(0);
    detach();
    await vi.advanceTimersByTimeAsync(2_000);
    expect(onChange).not.toHaveBeenCalled();
    expect(server.subscribers('orders:42')).toBe(0);
  });
});

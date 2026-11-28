import { QueryClient, QueryObserver } from '@tanstack/react-query';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { createRealtimeClient } from '@djangocfg/realtime';
import { createMockServer } from '@djangocfg/realtime/testing';

import { REALTIME_META_KEY, bridgeQueryCache } from './queryRealtime';

beforeEach(() => {
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
});

function setup() {
  const server = createMockServer({ ping: 0 });
  const client = createRealtimeClient({ url: server.url, WebSocket: server.WebSocket, random: () => 0, wake: () => () => {} });
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false, staleTime: Infinity } } });
  return { server, client, queryClient };
}

/** What a generated hook does: the query's options, with `meta.realtimeTopics` from `runtime/realtime-query.ts`. */
function observe(queryClient: QueryClient, key: unknown[], topics: string[] | null) {
  const queryFn = vi.fn(async () => ({ n: queryFn.mock.calls.length }));
  const observer = new QueryObserver(queryClient, {
    queryKey: key,
    queryFn,
    ...(topics ? { meta: { [REALTIME_META_KEY]: topics } } : {}),
  });
  const unsubscribe = observer.subscribe(() => {});
  return { queryFn, unsubscribe };
}

const settle = () => vi.advanceTimersByTimeAsync(300);

describe('bridgeQueryCache', () => {
  it('refetches a tagged query on a message and on a gap, and leaves an untagged one alone', async () => {
    const { server, client, queryClient } = setup();
    const tagged = observe(queryClient, ['/apix/realtime_demo/pings/'], ['demo.pings']);
    const untagged = observe(queryClient, ['/cfg/accounts/profile/'], null);
    const stop = bridgeQueryCache(queryClient, client);
    await settle();
    expect(server.subscribers('demo.pings')).toBe(1);

    // The first fetch, plus one when the subscription went live (a publication between them would be lost).
    const afterLive = tagged.queryFn.mock.calls.length;
    expect(afterLive).toBeGreaterThanOrEqual(1);
    expect(untagged.queryFn).toHaveBeenCalledTimes(1);

    server.publish('demo.pings', { id: 1 });
    server.publish('demo.pings', { id: 2 });
    await settle();
    expect(tagged.queryFn).toHaveBeenCalledTimes(afterLive + 1); // one refetch per burst

    server.bumpEpoch('demo.pings');
    await settle();
    expect(tagged.queryFn).toHaveBeenCalledTimes(afterLive + 2);
    expect(untagged.queryFn).toHaveBeenCalledTimes(1);

    stop();
    tagged.unsubscribe();
    untagged.unsubscribe();
  });

  it('subscribes a topic only while a tagged query has an observer, and releases it after the last one goes', async () => {
    const { server, client, queryClient } = setup();
    const stop = bridgeQueryCache(queryClient, client);
    await settle();
    expect(server.connections).toBe(0);

    const first = observe(queryClient, ['/apix/realtime_demo/pings/', { page: 1 }], ['demo.pings']);
    const second = observe(queryClient, ['/apix/realtime_demo/pings/', { page: 2 }], ['demo.pings']);
    await settle();
    expect(server.subscribers('demo.pings')).toBe(1);

    first.unsubscribe();
    await vi.advanceTimersByTimeAsync(2_000);
    expect(server.subscribers('demo.pings')).toBe(1); // the second still watches it

    second.unsubscribe();
    await vi.advanceTimersByTimeAsync(1_000);
    expect(server.subscribers('demo.pings')).toBe(1); // the client's delayed release (1.5 s) has not run yet
    await vi.advanceTimersByTimeAsync(1_000);
    expect(server.subscribers('demo.pings')).toBe(0);

    // The queries are still cached (gcTime), with no observer: a message refetches nothing.
    const calls = second.queryFn.mock.calls.length;
    server.publish('demo.pings', { id: 3 });
    await settle();
    expect(second.queryFn).toHaveBeenCalledTimes(calls);

    await vi.advanceTimersByTimeAsync(31_500);
    expect(server.connections).toBe(0);
    stop();
  });

  it('opens no socket when no query is tagged', async () => {
    const { server, client, queryClient } = setup();
    const untagged = observe(queryClient, ['/cfg/accounts/profile/'], null);
    const stop = bridgeQueryCache(queryClient, client);
    await vi.advanceTimersByTimeAsync(60_000);
    expect(server.connections).toBe(0);
    stop();
    untagged.unsubscribe();
  });
});

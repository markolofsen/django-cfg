import { watchTopics } from '@djangocfg/realtime';

import type { Query, QueryClient } from '@tanstack/react-query';
import type { RealtimeClient, WatchTopicsOptions } from '@djangocfg/realtime';

/**
 * The `meta` key a generated query carries its topics under: the concrete topic names of the operation's
 * `invalidated_by` (`x-realtime-invalidates`), written by the generated `runtime/realtime-query.ts`.
 */
export const REALTIME_META_KEY = 'realtimeTopics';

/** The topics a query is tagged with; `[]` for an untagged query. */
export function topicsOfQuery(query: Pick<Query, 'meta'>): string[] {
  const topics = query.meta?.[REALTIME_META_KEY];
  return Array.isArray(topics) ? topics.filter((topic): topic is string => typeof topic === 'string') : [];
}

const SYNC_EVENTS = new Set(['added', 'removed', 'observerAdded', 'observerRemoved', 'observerOptionsUpdated']);

/**
 * Keeps the realtime subscriptions in step with the QueryCache: a topic is subscribed while at least one query
 * tagged with it has an observer (a mounted hook), and released when the last one goes. The client's own delayed
 * unsubscribe (1.5 s) absorbs a remount. A message, a gap or a fresh subscription going live invalidates the
 * queries tagged with that topic, once per burst (`watchTopics`). Returns the function that stops it all.
 */
export function bridgeQueryCache(
  queryClient: QueryClient,
  client: RealtimeClient,
  options: WatchTopicsOptions = {},
): () => void {
  const cache = queryClient.getQueryCache();
  const watched = new Map<string, () => void>();

  const invalidate = (topic: string) => {
    void queryClient.invalidateQueries({ predicate: (query) => topicsOfQuery(query).includes(topic) });
  };

  const sync = () => {
    const wanted = new Set<string>();
    for (const query of cache.getAll()) {
      if (query.getObserversCount() === 0) continue;
      for (const topic of topicsOfQuery(query)) wanted.add(topic);
    }
    for (const [topic, release] of watched) {
      if (wanted.has(topic)) continue;
      watched.delete(topic);
      release();
    }
    for (const topic of wanted) {
      if (!watched.has(topic)) watched.set(topic, watchTopics(client, [topic], () => invalidate(topic), options));
    }
  };

  // Hooks below mount before this effect runs: their queries are already in the cache.
  sync();
  const unsubscribe = cache.subscribe((event) => {
    if (SYNC_EVENTS.has(event.type)) sync();
  });
  return () => {
    unsubscribe();
    for (const release of watched.values()) release();
    watched.clear();
  };
}

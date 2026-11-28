import { systemClock } from './socket/environment';

import type { RealtimeClient } from './realtime-client';
import type { Clock, TimerHandle } from './socket/environment';

export interface WatchTopicsOptions {
  /** Events closer together than this cause one `onChange`. Default 250 ms. */
  windowMs?: number;
  clock?: Clock;
}

export const DEFAULT_WATCH_WINDOW_MS = 250;

/**
 * "Something under these topics changed": subscribes each topic and calls
 * `onChange` once per burst of events or gaps, at the end of the window, and
 * once when a subscription goes live from the head. For caches that refetch
 * instead of folding events: `@djangocfg/layouts` invalidates the React Query
 * queries tagged with the topic (`meta.realtimeTopics`). Gaps already arrive jittered from the client.
 * Returns the function that releases every subscription.
 */
export function watchTopics(
  client: RealtimeClient,
  topics: readonly string[],
  onChange: () => void,
  options: WatchTopicsOptions = {},
): () => void {
  const clock = options.clock ?? systemClock;
  const windowMs = options.windowMs ?? DEFAULT_WATCH_WINDOW_MS;
  let timer: TimerHandle | null = null;
  let active = true;

  const schedule = () => {
    if (!active || timer !== null) return;
    timer = clock.setTimeout(() => {
      timer = null;
      if (active) onChange();
    }, windowMs);
  };
  // `onLive`: a fresh subscription starts at the head, so a publication between the caller's
  // read and the `sub_ok` would be lost without one refetch here.
  const releases = topics.map((topic) =>
    client.subscribe(topic, { onEvent: schedule, onGap: schedule, onLive: schedule }),
  );

  return () => {
    active = false;
    if (timer !== null) clock.clearTimeout(timer);
    timer = null;
    for (const release of releases) release();
  };
}

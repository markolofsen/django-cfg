import type { ProgressEngine } from '../engine/types';
import { clickDestination } from './linkClick';

export interface TriggerOptions {
  engine: ProgressEngine;
  /** Whether a navigation from `from` to `to` shows the bar. */
  shouldStart: (from: URL, to: URL) => boolean;
}

/**
 * Start the bar on link clicks; drop it on `pagehide` and when a page comes back from the
 * back-forward cache, so a frozen bar is never restored. Completion is not decided here:
 * the router wiring calls `engine.done()` when the navigation commits.
 */
export function attachRouteProgressTriggers({ engine, shouldStart }: TriggerOptions): () => void {
  const onClick = (event: MouseEvent) => {
    const to = clickDestination(event, window.location.href);
    if (to && shouldStart(new URL(window.location.href), to)) engine.start();
  };
  const reset = () => engine.cancel();

  document.addEventListener('click', onClick);
  window.addEventListener('pagehide', reset);
  window.addEventListener('pageshow', reset);
  return () => {
    document.removeEventListener('click', onClick);
    window.removeEventListener('pagehide', reset);
    window.removeEventListener('pageshow', reset);
  };
}

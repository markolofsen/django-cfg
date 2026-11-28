import { useSyncExternalStore } from "react";
import type { Style } from "@dicebear/core";

import { type AvatarKind, styleForSeed } from "../registry/corpora";
import { drawAvatar } from "./draw";

/**
 * Resolve a seed to drawn SVG, loading the style package on demand.
 *
 * The cache is module-level and keyed by STYLE, not by seed: a style is a large
 * import and a handful serve the whole console, while seeds are unbounded — one
 * per contact. Caching per seed would grow without limit to save arithmetic that
 * costs microseconds.
 *
 * Exposed through `useSyncExternalStore` because the cache IS external state
 * shared by every avatar on the page. An effect-plus-counter version of this
 * drew only the first row of a mixed list: a component mounting while another's
 * import was already in flight subscribed after that promise had resolved, so
 * nothing ever told it to re-render. The store model has no such window —
 * subscribers are notified from one place, after the cache is written.
 */
type LoadedStyle = Style<Record<string, unknown>>;

const cache = new Map<string, LoadedStyle>();
const inFlight = new Map<string, Promise<void>>();
const listeners = new Set<() => void>();

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

function ensureLoaded(styleId: string, load: () => Promise<LoadedStyle>) {
  if (cache.has(styleId) || inFlight.has(styleId)) return;
  const pending = load()
    .then((style) => {
      cache.set(styleId, style);
    })
    .finally(() => {
      inFlight.delete(styleId);
      // Every avatar re-reads the cache, not just the one that triggered the
      // import: a dozen rows sharing a style must all appear together.
      for (const listener of listeners) listener();
    });
  inFlight.set(styleId, pending);
}

/**
 * `null` while the style is still arriving; the caller paints a placeholder.
 *
 * Returns synchronously once the style is cached, which is the common case after
 * the first row of a corpus — a scrolled roster does not flash a placeholder per
 * row.
 */
export function useAvatarSvg(kind: AvatarKind, seed: string, size: number): string | null {
  const entry = styleForSeed(kind, seed);
  // The snapshot must be a STABLE reference for an unchanged cache, or
  // `useSyncExternalStore` re-renders forever. A style object from the map is
  // stable; a derived string would not be.
  const style = useSyncExternalStore(
    subscribe,
    () => cache.get(entry.id),
    () => cache.get(entry.id),
  );

  if (!style) {
    // Kicked off during render rather than in an effect so the request starts on
    // the first paint instead of one frame later. It is idempotent and touches
    // no component state, so a double-invoked render costs one map lookup.
    ensureLoaded(entry.id, entry.load);
    return null;
  }

  // `drawAvatar` owns the markup rewrites, shared with the server renderer.
  return drawAvatar(style, seed, size);
}

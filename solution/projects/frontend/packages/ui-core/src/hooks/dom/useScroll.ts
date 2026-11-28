'use client';

/**
 * useScroll — reactive snapshot of `scrollX` / `scrollY` for window or any
 * scrollable element.
 *
 * WHY:
 *   The DOM exposes scroll position via mutating `Element.scrollTop` /
 *   `Element.scrollLeft`, with the only signal being a flood of `scroll`
 *   events. To bridge this to React safely we:
 *
 *     1. **`useSyncExternalStore`** — the React-19-blessed primitive for
 *        external mutable sources. Solves SSR (`getServerSnapshot` returns
 *        zeros) and concurrent-mode tearing for free. Existing libraries
 *        (`react-use`, `usehooks-ts`, `@uidotdev/usehooks`) all predate
 *        this API and use plain `useState` + `useEffect`, which costs
 *        them re-renders on every frame at rest if their equality bailout
 *        is wrong (see react-use issue #1473).
 *
 *     2. **rAF-throttled writes, not subscribes** — scroll fires up to
 *        ~120 events/s on a Magic Trackpad. Reading `scrollX` is cheap
 *        but waking React isn't. We coalesce to one snapshot per frame
 *        per target, then notify subscribers once.
 *
 *     3. **Module-level store keyed by EventTarget** — many components
 *        on a page subscribe to the same `window` scroll. Without a
 *        shared store you'd attach N listeners and run rAF N times per
 *        frame. The store deduplicates: one listener + one rAF per
 *        unique target, regardless of subscriber count.
 *
 *     4. **`{ passive: true }`** — non-passive scroll listeners block
 *        compositor scrolling on mobile (Chrome warns about this in
 *        DevTools). Always opt in.
 *
 * @example
 *   const { y, direction, isScrolling } = useScroll();
 *   <header className={direction === 'down' && isScrolling ? 'hidden' : ''} />
 *
 * @example
 *   // Scroll inside a panel:
 *   const ref = useRef<HTMLDivElement>(null);
 *   const { y } = useScrollPosition(ref);
 *
 * @example
 *   // Subscribe to ONE field — re-renders only when direction flips,
 *   // not on every pixel of scroll:
 *   const direction = useScrollDirection();
 */

import { useCallback, useMemo, useSyncExternalStore, type RefObject } from 'react';

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

export type ScrollDirection = 'up' | 'down' | 'left' | 'right' | null;

/** Frozen snapshot returned to React. Identity changes only when contents change. */
export interface ScrollSnapshot {
  /** Horizontal scroll offset in CSS pixels. */
  x: number;
  /** Vertical scroll offset in CSS pixels. */
  y: number;
  /**
   * Direction of the LAST delta. Resets to `null` after `isScrolling`
   * falls to `false`. For cumulative direction (e.g. hide-on-scroll
   * navbar), build on top of this.
   */
  direction: ScrollDirection;
  /** True until 150 ms have passed since the last scroll event. */
  isScrolling: boolean;
}

export type ScrollTarget = RefObject<Element | null> | Window;

// ─────────────────────────────────────────────────────────────────────────────
// SSR snapshot
// ─────────────────────────────────────────────────────────────────────────────

const SSR_SNAPSHOT: ScrollSnapshot = Object.freeze({
  x: 0,
  y: 0,
  direction: null,
  isScrolling: false,
});

// ─────────────────────────────────────────────────────────────────────────────
// Per-target store
// ─────────────────────────────────────────────────────────────────────────────

interface TargetState {
  snapshot: ScrollSnapshot;
  subscribers: Set<() => void>;
  rafId: number | null;
  idleTimer: ReturnType<typeof setTimeout> | null;
  removeListener: () => void;
}

/**
 * One entry per unique scroll source on the page (typically just `window`,
 * plus any scrollable panels). Lives at module scope so every consumer
 * shares the same listener + rAF.
 */
const stores = new WeakMap<EventTarget, TargetState>();

const IDLE_MS = 150;

/** Reads the current scroll offsets from a target. */
function readScroll(target: EventTarget): { x: number; y: number } {
  if (target === window) {
    return { x: window.scrollX, y: window.scrollY };
  }
  const el = target as Element;
  return { x: el.scrollLeft, y: el.scrollTop };
}

function deriveDirection(
  prev: { x: number; y: number },
  next: { x: number; y: number }
): ScrollDirection {
  const dx = next.x - prev.x;
  const dy = next.y - prev.y;
  // Vertical wins on ties — most pages scroll vertically.
  if (Math.abs(dy) >= Math.abs(dx)) {
    if (dy > 0) return 'down';
    if (dy < 0) return 'up';
    return null;
  }
  if (dx > 0) return 'right';
  if (dx < 0) return 'left';
  return null;
}

function getOrCreateStore(target: EventTarget): TargetState {
  const existing = stores.get(target);
  if (existing) return existing;

  // Initial read so the first snapshot is correct (don't wait for first event).
  const initial = readScroll(target);

  const state: TargetState = {
    snapshot: Object.freeze({
      x: initial.x,
      y: initial.y,
      direction: null,
      isScrolling: false,
    }),
    subscribers: new Set(),
    rafId: null,
    idleTimer: null,
    removeListener: () => {},
  };

  const onScroll = () => {
    // Coalesce bursts of scroll events to one rAF tick. Reading scrollX
    // mid-event is cheap, but notifying React isn't.
    if (state.rafId !== null) return;
    state.rafId = requestAnimationFrame(() => {
      state.rafId = null;
      const next = readScroll(target);
      const direction = deriveDirection(state.snapshot, next);
      // Equality bailout: if nothing changed AND we're already marked as
      // scrolling, skip the snapshot mint and the React notification.
      // This catches duplicate scroll events on the same frame.
      if (
        next.x === state.snapshot.x &&
        next.y === state.snapshot.y &&
        state.snapshot.isScrolling
      ) {
        return;
      }
      state.snapshot = Object.freeze({
        x: next.x,
        y: next.y,
        direction,
        isScrolling: true,
      });
      // Reset idle timer — fires once user pauses for IDLE_MS.
      if (state.idleTimer !== null) clearTimeout(state.idleTimer);
      state.idleTimer = setTimeout(() => {
        state.idleTimer = null;
        state.snapshot = Object.freeze({
          x: state.snapshot.x,
          y: state.snapshot.y,
          // Direction also resets — fresh scroll restarts the signal.
          direction: null,
          isScrolling: false,
        });
        for (const cb of state.subscribers) cb();
      }, IDLE_MS);
      for (const cb of state.subscribers) cb();
    });
  };

  target.addEventListener('scroll', onScroll, { passive: true, capture: false });
  state.removeListener = () => {
    target.removeEventListener('scroll', onScroll, { capture: false });
  };

  stores.set(target, state);
  return state;
}

function teardownStore(target: EventTarget): void {
  const state = stores.get(target);
  if (!state || state.subscribers.size > 0) return;
  state.removeListener();
  if (state.rafId !== null) cancelAnimationFrame(state.rafId);
  if (state.idleTimer !== null) clearTimeout(state.idleTimer);
  stores.delete(target);
}

// ─────────────────────────────────────────────────────────────────────────────
// Subscribe / getSnapshot factories
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Resolves a `RefObject | Window | undefined` to an actual EventTarget at
 * call time. Must be called inside subscribe/getSnapshot — if the ref's
 * `.current` flips between renders, we want to follow it.
 */
function resolveTarget(target: ScrollTarget | undefined): EventTarget | null {
  if (typeof window === 'undefined') return null;
  if (!target || target === window) return window;
  // RefObject — read current at call site, may be null before mount.
  return (target as RefObject<Element | null>).current ?? null;
}

function subscribeFactory(target: ScrollTarget | undefined) {
  return (onChange: () => void): (() => void) => {
    const t = resolveTarget(target);
    if (!t) return () => {};
    const state = getOrCreateStore(t);
    state.subscribers.add(onChange);
    return () => {
      state.subscribers.delete(onChange);
      teardownStore(t);
    };
  };
}

function getSnapshotFactory(target: ScrollTarget | undefined) {
  return (): ScrollSnapshot => {
    const t = resolveTarget(target);
    if (!t) return SSR_SNAPSHOT;
    const state = stores.get(t);
    return state ? state.snapshot : SSR_SNAPSHOT;
  };
}

const getServerSnapshot = (): ScrollSnapshot => SSR_SNAPSHOT;

// ─────────────────────────────────────────────────────────────────────────────
// Public hooks
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Reactive snapshot of scroll position + direction + isScrolling for the
 * given target (default: `window`). Returns a stable object reference until
 * something actually changes — safe to put in deps arrays.
 *
 * If you only need ONE field, prefer `useScrollPosition`,
 * `useScrollDirection`, or `useIsScrolling` — they subscribe to the same
 * underlying store but let React skip re-renders when other fields change.
 */
export function useScroll(target?: ScrollTarget): ScrollSnapshot {
  // useMemo, not useCallback: these are factory RESULTS, not inline functions.
  const subscribe = useMemo(() => subscribeFactory(target), [target]);
  const getSnapshot = useMemo(() => getSnapshotFactory(target), [target]);
  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}

/**
 * Subscribe to just `{x, y}`. Re-renders only when the scroll offsets
 * change — direction flips and isScrolling transitions are ignored.
 */
export function useScrollPosition(target?: ScrollTarget): { x: number; y: number } {
  const subscribe = useMemo(() => subscribeFactory(target), [target]);
  const getServerXY = useCallback(() => SSR_XY, []);
  const getXY = useCallback(() => {
    const snap = getSnapshotFactory(target)();
    // Cache by snapshot identity — every snapshot is frozen, so identity
    // change ⇔ content change. Avoids minting a new {x,y} on every read.
    return positionCache.get(snap) ?? cachePosition(snap);
  }, [target]);
  return useSyncExternalStore(subscribe, getXY, getServerXY);
}

const SSR_XY = Object.freeze({ x: 0, y: 0 });
const positionCache = new WeakMap<ScrollSnapshot, { x: number; y: number }>();
function cachePosition(snap: ScrollSnapshot): { x: number; y: number } {
  const xy = Object.freeze({ x: snap.x, y: snap.y });
  positionCache.set(snap, xy);
  return xy;
}

/**
 * Subscribe to just the direction signal. Re-renders only when direction
 * flips (e.g. user reverses scroll).
 */
export function useScrollDirection(target?: ScrollTarget): ScrollDirection {
  const subscribe = useMemo(() => subscribeFactory(target), [target]);
  const getDirection = useCallback(
    () => getSnapshotFactory(target)().direction,
    [target]
  );
  const getServerDirection = useCallback((): ScrollDirection => null, []);
  return useSyncExternalStore(subscribe, getDirection, getServerDirection);
}

/**
 * `true` while the user is actively scrolling, `false` after a 150 ms
 * idle gap. Useful for hiding hover overlays while scrolling.
 */
export function useIsScrolling(target?: ScrollTarget): boolean {
  const subscribe = useMemo(() => subscribeFactory(target), [target]);
  const getIsScrolling = useCallback(
    () => getSnapshotFactory(target)().isScrolling,
    [target]
  );
  const getServerIsScrolling = useCallback(() => false, []);
  return useSyncExternalStore(subscribe, getIsScrolling, getServerIsScrolling);
}

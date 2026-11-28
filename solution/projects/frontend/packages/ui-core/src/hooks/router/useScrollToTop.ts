'use client';

/**
 * useScrollToTop — land at the top of the page after a forward navigation.
 *
 * WHY THIS EXISTS AT ALL — Next.js App Router already scrolls, sometimes
 *
 * `layout-router.tsx` walks the navigated segment looking for an element to
 * scroll to, and **gives up silently** in two cases that are ordinary in our
 * apps:
 *
 *   1. It takes the segment's first DOM node and skips it when the node is
 *      `position: sticky|fixed` OR when `getBoundingClientRect()` is all
 *      zeroes — then moves to `nextElementSibling`, and `return`s outright
 *      when there is none. A page whose root is `display: contents` (a width
 *      wrapper), or whose first child renders `null`, `<script type=
 *      "application/ld+json">`, or any other zero-box node, therefore gets no
 *      scroll at all.
 *   2. Having found a node, it exits early when that node's top edge is
 *      ALREADY within the viewport. Land mid-page on a long route whose next
 *      route starts with a tall block, and the check passes while the visitor
 *      is looking at the middle of the new page.
 *
 * Both are position-dependent, which is why the bug reads as intermittent:
 * clicking from the top of a page (what an automated run usually does) hits
 * neither branch, so the symptom only shows up when a person scrolls first.
 *
 * WHAT IT DELIBERATELY DOES NOT DO
 *
 * - **Back/forward are left alone.** The browser restores the previous scroll
 *   position on a `popstate`, and overriding that is a worse bug than the one
 *   being fixed. Only `pushState`/`replaceState` navigations scroll.
 * - **`#hash` links are left alone.** A URL naming an anchor has already said
 *   where it wants to land.
 * - **Query-only changes are left alone.** Filters, pagination and tab state
 *   write the query string; yanking the visitor to the top as they tick a
 *   checkbox is the complaint this hook would otherwise cause. Only a
 *   `pathname` change scrolls.
 *
 * It is idempotent with Next's own handler: when Next succeeds we are already
 * at the top and the write is a no-op.
 *
 * @example
 *   // Once, at the app root — `BaseApp` already does this for Next.js hosts.
 *   useScrollToTop();
 */

import { useEffect, useRef } from 'react';

import { useRouteProgress } from '../../route-progress';
import { NAVIGATE_EVENT, patchHistoryOnce } from './useLocation';

export interface UseScrollToTopOptions {
  /** Turn the behaviour off without unmounting the host. Default: true. */
  enabled?: boolean;
  /**
   * Scroll animation. Default `'auto'` (instant), matching a hard navigation.
   * `'smooth'` animates a full page height on every route change, which reads
   * as lag rather than polish.
   */
  behavior?: ScrollBehavior;
}

/**
 * Scrolls the window to the top after each forward navigation to a new path.
 * Mount ONCE per app — a second mount just writes `scrollTo(0, 0)` twice.
 */
export function useScrollToTop({
  enabled = true,
  behavior = 'auto',
}: UseScrollToTopOptions = {}): void {
  /**
   * The path we last saw. Seeded on mount rather than from `''`, so the first
   * paint does not count as a navigation — that would fight the browser's own
   * restoration on a reload.
   */
  const lastPathRef = useRef<string | null>(null);
  // The page's switches (`useNavigationBehavior`) live in the app's RouteProgressProvider.
  const progress = useRouteProgress();
  const progressRef = useRef(progress);
  progressRef.current = progress;

  useEffect(() => {
    if (!enabled || typeof window === 'undefined') return;

    // `pushState`/`replaceState` do not emit an event on their own. Without
    // this the listener below is subscribed to something nothing dispatches.
    patchHistoryOnce();
    lastPathRef.current = window.location.pathname;

    /*
     * NAVIGATE_EVENT only, and that is what keeps back/forward working: the
     * patch in `useLocation` dispatches it from `pushState`/`replaceState`
     * exclusively, so a `popstate` never reaches this handler and the
     * browser's restored position is never overwritten. Subscribing to
     * `popstate` here — or to `hashchange` — would undo exactly that.
     */
    const onNavigate = () => {
      const { pathname, hash } = window.location;
      const changedPath = pathname !== lastPathRef.current;
      lastPathRef.current = pathname;

      // Query-only or state-only writes: the visitor stays where they are.
      if (!changedPath) return;
      // The page asked to keep its position (`useNavigationBehavior`).
      if (progressRef.current?.behavior.get().scroll === false) return;
      // The URL names an anchor; it has already said where to land.
      if (hash) return;

      /*
       * Deferred by one frame, and this is load-bearing. Our navigate event
       * fires from a microtask right after `pushState`, while the destination
       * is still the OLD document — React has not committed the new segment
       * yet. Scrolling then is correct but immediately undone: Next's own
       * handler runs on the commit that follows and may scroll back down to
       * an element it found mid-page. Running after paint means we write
       * last, over a document whose real height is known.
       */
      requestAnimationFrame(() => {
        window.scrollTo({ top: 0, left: 0, behavior });
      });
    };

    window.addEventListener(NAVIGATE_EVENT, onNavigate);
    return () => window.removeEventListener(NAVIGATE_EVENT, onNavigate);
  }, [enabled, behavior]);
}

/**
 * Keep the reader at the bottom when the SCROLLER changes height and the content does not.
 *
 * Root cause of "the history jumps when the input gets focus". `use-stick-to-bottom` observes the CONTENT element, so
 * it follows text that grows; it does not observe the scroller. When the keyboard opens (or the composer grows, or the
 * phone turns) the scroller gets shorter, `scrollTop` stays, and the newest messages are now below the fold: nothing
 * grew, so nothing followed. Worse, the browser scrolls the focused field into view in the same moment; the scroller
 * moves up, the library reads that as the reader scrolling up, "escapes" the lock, and from then on neither follows
 * nor shows the bottom.
 *
 * What this does, with the decisions in `core/screen/pin.ts`:
 *  - remembers whether the reader is within `PIN_THRESHOLD` of the bottom, from scroll events, EXCEPT those inside a
 *    settle window opened by a field gaining or losing focus or by the visual viewport changing (those are the browser's);
 *  - when the scroller resizes or the viewport moves and the reader was pinned, re-pins instantly and tells the library
 *    to ignore escapes for the window. A reader who scrolled up on purpose is not pinned, so nothing happens to them.
 */

import { useCallback, useRef } from "react";

import { PIN_THRESHOLD, SETTLE_MS, nextPinned } from "../../core/screen";

export interface HoldBottomOptions {
  /** Re-pin for `ms` (the stick-to-bottom engine's `holdBottom`). */
  readonly hold: (ms: number) => void;
  /** Distance from the bottom that still counts as pinned. */
  readonly threshold?: number;
}

const isField = (target: EventTarget | null): boolean =>
  target instanceof HTMLElement && (target.matches("textarea, input, select") || target.isContentEditable);

function attach(node: HTMLElement, hold: (ms: number) => void, threshold: number): () => void {
  let pinned = true;
  let settleUntil = 0;
  const settling = () => performance.now() < settleUntil;
  const metrics = () => ({ scrollHeight: node.scrollHeight, scrollTop: node.scrollTop, clientHeight: node.clientHeight });

  const open = () => {
    settleUntil = performance.now() + SETTLE_MS;
  };
  const follow = () => {
    if (pinned) hold(Math.max(settleUntil - performance.now(), 120));
  };
  const onScroll = () => {
    pinned = nextPinned(pinned, metrics(), settling(), threshold);
  };
  const onFocus = (event: FocusEvent) => {
    if (!isField(event.target)) return;
    open();
    follow();
  };
  const onViewport = () => {
    open();
    follow();
  };

  // Seed from the real position, in case the transcript opened already scrolled.
  pinned = nextPinned(true, metrics(), false, threshold);
  node.addEventListener("scroll", onScroll, { passive: true });
  document.addEventListener("focusin", onFocus);
  document.addEventListener("focusout", onFocus);
  const vv = window.visualViewport;
  vv?.addEventListener("resize", onViewport);
  const observer = new ResizeObserver(follow);
  observer.observe(node);
  return () => {
    node.removeEventListener("scroll", onScroll);
    document.removeEventListener("focusin", onFocus);
    document.removeEventListener("focusout", onFocus);
    vv?.removeEventListener("resize", onViewport);
    observer.disconnect();
  };
}

/** A ref callback for the SCROLLER; compose it with the one the stick-to-bottom engine needs. */
export function useHoldBottom({ hold, threshold = PIN_THRESHOLD }: HoldBottomOptions): (node: HTMLElement | null) => void {
  const stop = useRef<(() => void) | null>(null);
  const latest = useRef(hold);
  latest.current = hold;
  return useCallback(
    (node: HTMLElement | null) => {
      stop.current?.();
      stop.current = null;
      if (node && typeof ResizeObserver !== "undefined") stop.current = attach(node, (ms) => latest.current(ms), threshold);
    },
    [threshold],
  );
}

// Whether the reader is "at the bottom", and whether the view should follow it.
//
// The follow itself is `use-stick-to-bottom`'s (see `primitives/transcript/use-stick-to-bottom`). What the library cannot
// know is that the SCROLLER can change height without the content changing: an on-screen keyboard, a growing
// composer, a rotation. The bottom then moves away under a reader who never scrolled. These two functions
// decide, without a DOM, whether that reader was at the bottom and so must be taken back to it.

/** Distance from the newest message that still counts as "at the bottom" (px). */
export const PIN_THRESHOLD = 80;

/** How long after a focus or a viewport change the browser's own scrolling is not read as the reader leaving (ms). The iOS keyboard animates for about 400. */
export const SETTLE_MS = 700;

export interface ScrollMetrics {
  readonly scrollHeight: number;
  readonly scrollTop: number;
  readonly clientHeight: number;
}

export function distanceFromBottom(m: ScrollMetrics): number {
  return Math.max(0, m.scrollHeight - m.scrollTop - m.clientHeight);
}

/**
 * The reader's intent, updated on each scroll event.
 *
 * While `settling`, a scroll event is the BROWSER's (it scrolls a focused field into view, clamps a shrinking box),
 * not the reader's, so the previous intent stands. Outside it, being within `threshold` of the bottom is being pinned
 * and anything further is a reader who scrolled up on purpose.
 */
export function nextPinned(previous: boolean, m: ScrollMetrics, settling: boolean, threshold: number = PIN_THRESHOLD): boolean {
  if (settling) return previous;
  return distanceFromBottom(m) <= threshold;
}

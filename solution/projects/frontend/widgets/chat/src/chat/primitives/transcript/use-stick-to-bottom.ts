/**
 * Following the bottom, delegated to `use-stick-to-bottom`.
 *
 * This was ours, twice, and both versions had the same class of defect: an
 * INSTANT write to `scrollTop` on every growth. A hard fling landing on the
 * bottom edge then visibly shook — measured at 5–12 direction reversals with an
 * 8–23px swing — because the write, the engine's own settle and the resulting
 * scroll event chase each other inside one frame. Neither a tolerance around
 * the target nor rounding the box's fractional height fixed it; a write-trap
 * proved the hook was not even the one writing during the shake.
 *
 * The library answers it structurally rather than by tuning: it animates toward
 * the bottom with a damped spring, so there is no single frame that jumps, and
 * it remembers the position it last wrote (`ignoreScrollToTop`) so its own echo
 * is never mistaken for the reader scrolling. It also suspends following while
 * a text selection is in progress, which no amount of gesture-watching here
 * would have covered.
 *
 * What stays ours is the SHAPE of the return value: `Transcript` consumes
 * `{ ref, onScroll, isPinned, scrollToBottom }`, and keeping that means the
 * primitive did not have to learn about a second element.
 */

import { useCallback, type UIEvent } from "react";
import { useStickToBottom as useLibraryStickToBottom } from "use-stick-to-bottom";

export interface StickToBottom {
  /** The SCROLLER. */
  readonly ref: (node: HTMLDivElement | null) => void;
  /** The element wrapping the rows, which is what actually changes height. */
  readonly contentRef: (node: HTMLDivElement | null) => void;
  readonly onScroll: (event: UIEvent<HTMLDivElement>) => void;
  /** False while the user is reading history — render a "jump to latest" control. */
  readonly isPinned: boolean;
  readonly scrollToBottom: () => void;
  /**
   * Re-pin to the bottom for `ms`, instantly, and treat any scroll the BROWSER makes in that time (focus scrolling,
   * keyboard clamping) as not the reader's. Used by `useHoldBottom`.
   */
  readonly holdBottom: (ms: number) => void;
}

/**
 * @param revision unused, and kept only so callers need not change. The library
 *   watches the content element with a ResizeObserver, which sees streamed text
 *   grow a row as readily as it sees a row appear — the count was always a
 *   proxy for exactly that.
 */
export function useStickToBottom(_revision: number): StickToBottom {
  const instance = useLibraryStickToBottom({
    // Growth is ANIMATED. `instant` here is what produced the shake: it lands
    // the view on the target in one frame, so the engine's own settle reads as
    // a bounce rather than as part of a motion.
    resize: "smooth",
    // Arrival is INSTANT, and the asymmetry is the point. Opening a room is not
    // motion the reader is following — there is nothing on screen yet to track —
    // so animating it scrolls a transcript they never asked to watch, every
    // single time they switch. The bottom is simply where the room starts.
    initial: "instant",
  });

  const { scrollRef, contentRef, isAtBottom, scrollToBottom } = instance;

  const ref = useCallback(
    (node: HTMLDivElement | null) => {
      scrollRef(node);
    },
    [scrollRef],
  );

  const content = useCallback(
    (node: HTMLDivElement | null) => {
      contentRef(node);
    },
    [contentRef],
  );

  // The library listens on the element itself, so nothing has to happen here.
  // Kept because `Transcript` passes it to the scroller and a missing handler
  // would be a silent behaviour change rather than a type error.
  const onScroll = useCallback(() => {}, []);

  const jump = useCallback(() => {
    void scrollToBottom();
  }, [scrollToBottom]);

  const hold = useCallback(
    (ms: number) => {
      void scrollToBottom({ animation: "instant", ignoreEscapes: true, duration: ms });
    },
    [scrollToBottom],
  );

  return { ref, contentRef: content, onScroll, isPinned: isAtBottom, scrollToBottom: jump, holdBottom: hold };
}

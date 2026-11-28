/**
 * Does this element have more content than the height it is allowed?
 *
 * Answers the question by measuring the thing itself rather than by estimating
 * from what is inside it. A message is an array of parts, not a string: an image
 * or a table contributes almost no characters at a large height, and a code
 * fence keeps its characters while losing its shape. Any character count is
 * therefore a proxy for a proxy, and the element already knows the answer.
 *
 * Reports only. It never writes a height — the clamp is a CSS `max-height` the
 * caller owns, which is what makes the measurement honest: while collapsed the
 * element IS clipped, so `scrollHeight > clientHeight` is exactly the question.
 */

import { useCallback, useLayoutEffect, useState, type RefObject } from "react";

/**
 * @param ref the clamped element — the one carrying `max-height`.
 * @param expanded whether the clamp is currently lifted. Load-bearing: see the
 *   collapse-first note below.
 * @param deps a value that changes when the content does, so a streamed message
 *   re-measures as it grows.
 */
export function useOverflows(
  ref: RefObject<HTMLElement | null>,
  expanded: boolean,
  deps: unknown,
): boolean {
  const [overflows, setOverflows] = useState(false);

  const measure = useCallback(() => {
    const node = ref.current;
    if (node === null) return;

    // Collapse first. `scrollHeight` and `clientHeight` are equal while the
    // clamp is lifted, so measuring in the expanded state reports "fits" for
    // every message and the control disappears the moment it is used. The
    // composer's autosize carries the same ordering for the same reason.
    //
    // Removing the property rather than setting a value returns the element to
    // whatever the stylesheet says, so this never has to know the budget.
    const lifted = expanded;
    const previous = node.style.maxHeight;
    if (lifted) node.style.maxHeight = "";

    setOverflows(node.scrollHeight > node.clientHeight);

    if (lifted) node.style.maxHeight = previous;
  }, [ref, expanded]);

  // A layout effect, not an effect: the trigger must be present in the same
  // paint as the clipped text, or a long message shows one frame with no way to
  // open it.
  useLayoutEffect(measure, [measure, deps]);

  // Content can also change height without the deps changing — a font loads, an
  // image decodes, the window narrows and the text rewraps. The element itself
  // is the only reliable signal for those.
  useLayoutEffect(() => {
    const node = ref.current;
    if (node === null) return;
    if (typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(measure);
    observer.observe(node);
    return () => observer.disconnect();
  }, [ref, measure]);

  return overflows;
}

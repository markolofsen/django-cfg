import { useCallback, useLayoutEffect, useRef, useState, type RefObject } from "react";

/**
 * Can the browser size a field to its own content?
 *
 * When it can, autosize is a CSS declaration and the measure-and-write cycle
 * below is dead weight — worse than dead, since writing `height` in JS overrides
 * what `field-sizing` computed. When it cannot (Firefox, Safari before 26) the
 * effect is the only implementation, so it stays.
 *
 * Read ONCE at module scope, not per keystroke: it is a property of the engine
 * and cannot change while the page is loaded. Guarded for SSR, where there is no
 * `CSS` object at all and the JS path is the safe assumption.
 */
export const FIELD_SIZING =
  typeof CSS !== "undefined" &&
  typeof CSS.supports === "function" &&
  CSS.supports("field-sizing", "content");

/**
 * Grow a textarea with its content, up to `maxRows`, then scroll.
 *
 * Beside `input.tsx` rather than inside it: the two share the node and nothing
 * else. `input.tsx` is a KEYBOARD component — paste, Enter-to-send and IME
 * composition all reason about what a keystroke means — while this measures
 * pixels and carries a module-scope feature-detection constant of its own.
 *
 * Runs as a layout effect, not an effect: the box must reach its final height
 * in the same paint as the text, or every keystroke shows one frame at the old
 * height. Keyed on the text so a PROGRAMMATIC change resizes too — sending
 * clears the draft, "attach as text" fills it, and neither is a keystroke.
 */
export function useAutosize(
  ref: RefObject<HTMLTextAreaElement | null>,
  text: string,
  maxRows: number,
): boolean {
  // More than one line, INCLUDING a soft-wrapped long one — which
  // `text.includes("\n")` cannot see and is what users actually type.
  const [multiline, setMultiline] = useState(false);
  // The field's width while the flag is OFF — the one width the wrap question
  // may be asked at. Learned from the field itself rather than configured, so a
  // host that lays the composer out differently needs no second number here.
  const compactWidth = useRef<number | null>(null);

  const resize = useCallback(() => {
    const node = ref.current;
    if (node === null) return;

    // Multiline, measured. Before the `field-sizing` return: the flag is about
    // rendered height either way, and after it this never runs on a modern
    // browser.
    //
    // Asked as a ROW COUNT rather than as a height comparison. `scrollHeight`
    // is an integer, so a fractional line height never divides evenly into it
    // and any "taller than one line" test needs a tolerance — the sort of
    // constant that is invisibly wrong on the one browser nobody checked.
    // Rounding the quotient puts the tolerance where it belongs: half a row,
    // whatever a row happens to measure.
    //
    // `scrollHeight` includes the field's own vertical padding, so the inset
    // comes off first — without it EVERY field reports as multiline.
    const probe = window.getComputedStyle(node);
    const rowHeight = Number.parseFloat(probe.lineHeight);
    if (!Number.isNaN(rowHeight) && rowHeight > 0) {
      const inset =
        Number.parseFloat(probe.paddingTop) + Number.parseFloat(probe.paddingBottom);
      const rowsAt = () => Math.round((node.scrollHeight - inset) / rowHeight);
      // Measured at the COMPACT width, always — never at the current one.
      //
      // The flag widens the field, so asking a wide field "do you wrap?" asks
      // about a width the answer itself created: the text fits, the flag drops,
      // the field narrows, the text wraps, the flag returns. Measured at 19
      // flips over 36 keystrokes, one per character.
      //
      // `compactWidth` is the width the field has while the flag is off, so the
      // question is always the stable one: does this text fit on one line THERE.
      const compact = compactWidth.current;
      if (compact === null || node.getBoundingClientRect().width <= compact) {
        compactWidth.current = node.getBoundingClientRect().width;
        setMultiline(rowsAt() > 1);
      } else {
        const restore = node.style.width;
        node.style.width = `${compact}px`;
        const wraps = rowsAt() > 1;
        node.style.width = restore;
        setMultiline(wraps);
      }
    }

    // The browser already sized the box from its content — measuring and
    // writing a pixel height on top would fight it, and writing `height` at all
    // defeats `field-sizing` outright.
    if (FIELD_SIZING) return;
    // Collapse first: scrollHeight never shrinks while the box is already tall
    // enough to hold the old text, so measuring without this makes the textarea
    // a one-way ratchet that only ever grows.
    node.style.height = "auto";
    const style = window.getComputedStyle(node);
    const lineHeight = Number.parseFloat(style.lineHeight);
    const vertical =
      Number.parseFloat(style.paddingTop) +
      Number.parseFloat(style.paddingBottom) +
      Number.parseFloat(style.borderTopWidth) +
      Number.parseFloat(style.borderBottomWidth);
    // `lineHeight: normal` parses to NaN; then there is no row unit to cap by,
    // and an unbounded box beats a box collapsed to zero.
    const cap = Number.isNaN(lineHeight) ? Number.POSITIVE_INFINITY : lineHeight * maxRows + vertical;
    const next = Math.min(node.scrollHeight, cap);
    node.style.height = `${next}px`;
    node.style.overflowY = node.scrollHeight > cap ? "auto" : "hidden";
  }, [ref, maxRows]);

  useLayoutEffect(resize, [resize, text]);

  /**
   * Follow the caret once the field scrolls internally.
   *
   * The browser does this for typing but NOT for a programmatic write, which is
   * what dictation is — `setText` from a speech callback left the box frozen
   * while the transcript grew past it.
   */
  useLayoutEffect(() => {
    const node = ref.current;
    if (node === null) return;
    if (node.scrollHeight <= node.clientHeight) return;
    // Only with the caret at the end: mid-text it would yank the view away from
    // what the user is editing.
    if (node.selectionEnd !== node.value.length) return;
    node.scrollTop = node.scrollHeight;
  }, [ref, text]);

  return multiline;
}

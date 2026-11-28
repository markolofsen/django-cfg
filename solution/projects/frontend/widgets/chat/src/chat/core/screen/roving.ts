/**
 * The transcript is ONE tab stop; arrows move within it.
 *
 * Without this, Tab walks every message, every tool card and every link before
 * reaching the composer — so on a transcript of any length a keyboard user
 * cannot reach the input at all. The APG calls it roving tabindex.
 *
 * The DOM part is three lines and lives in `primitives/`. What lives here is
 * the part that can be wrong: which index a key selects.
 */

export const CHAT_ITEM_ATTR = "data-chat-item";

/** Keys that move within the transcript, mapped to a target index. */
export type RovingKey = "ArrowDown" | "ArrowUp" | "Home" | "End";

export function isRovingKey(key: string): key is RovingKey {
  return key === "ArrowDown" || key === "ArrowUp" || key === "Home" || key === "End";
}

/**
 * Where a key moves the active row, or `null` when it moves nowhere.
 *
 * `null` — rather than "the same index" — is what lets the caller decide
 * whether to call `preventDefault()`. Swallowing ArrowDown at the last row
 * would stop the PAGE from scrolling, which is the browser behaviour a user at
 * the end of a transcript is relying on.
 */
export function nextIndex(key: RovingKey, active: number, count: number): number | null {
  if (count === 0) return null;

  const last = count - 1;
  // Clamped, never wrapped. Wrapping from the newest message to the first is
  // disorienting in a transcript, where position carries meaning — MUI X Chat
  // clamps here too.
  const target =
    key === "Home"
      ? 0
      : key === "End"
        ? last
        : Math.min(last, Math.max(0, active + (key === "ArrowDown" ? 1 : -1)));

  return target === active ? null : target;
}

/**
 * Keep the active index valid as the transcript grows and shrinks.
 *
 * Messages arrive while the user reads. An index that outlives its row leaves
 * EVERY row with `tabIndex={-1}` — the transcript silently stops being
 * reachable by Tab at all, and nothing about it looks broken.
 */
export function clampIndex(active: number, count: number): number {
  if (count === 0) return 0;
  return Math.min(count - 1, Math.max(0, active));
}

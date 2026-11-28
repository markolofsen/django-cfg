// Where an arrow key moves a menu cursor.
//
// May import: nothing.

/** Nothing is selected yet — the state a freshly opened menu is in. */
export const NO_ROW = -1;

/**
 * The next cursor position, or `NO_ROW` when the key does not move it.
 *
 * Movement WRAPS. The list is short and the user is aiming at one row, so
 * stopping at the end costs a direction change to reach what is one step the
 * other way.
 *
 * From nothing selected, Down opens at the top and Up at the BOTTOM: the last
 * row is then one keystroke away instead of `count - 1` of them.
 *
 * Pure, and separate from the hook binding it, because this package has no DOM
 * to render a hook into — the same reason the recall ladder is a pure module.
 */
export function nextRow(current: number, step: number, count: number): number {
  if (count === 0 || step === 0) return NO_ROW;
  if (current < 0) return step > 0 ? 0 : count - 1;
  return (current + step + count) % count;
}

/** The step an arrow key asks for; 0 for every other key. */
export function stepForKey(key: string): number {
  if (key === "ArrowDown") return 1;
  if (key === "ArrowUp") return -1;
  return 0;
}

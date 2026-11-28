// The picked-tool list as a SET, keyed by id.
//
// May import: ./tool-picks.

import type { ToolPick } from "./picks";

/**
 * Add a pick unless its id is already staged.
 *
 * Uniqueness belongs to the list, not to each caller: three paths write it —
 * the menu, a paste carrying a marker, a restored draft — and a rule enforced
 * at three call sites is one an unrelated fourth breaks. A duplicate is not
 * cosmetic either: `appendToolMarkers` would write the marker twice and the
 * model would read two requests.
 *
 * Returns the SAME array when nothing changes, so a no-op cannot re-render.
 */
export function addToolPick(
  picks: readonly ToolPick[],
  pick: ToolPick,
): readonly ToolPick[] {
  return picks.some((staged) => staged.id === pick.id) ? picks : [...picks, pick];
}

/** Add several, in order, each subject to the same rule. */
export function addToolPicks(
  picks: readonly ToolPick[],
  incoming: readonly ToolPick[],
): readonly ToolPick[] {
  return incoming.reduce(addToolPick, picks);
}

export function removeToolPick(picks: readonly ToolPick[], id: string): readonly ToolPick[] {
  return picks.filter((pick) => pick.id !== id);
}

/**
 * The menu's verb: staged ⇒ remove, absent ⇒ add.
 *
 * A toggle rather than an add because the menu row is the same control either
 * way — a second press has to mean "undo", and silently ignoring it reads as a
 * dead row.
 */
export function toggleToolPick(picks: readonly ToolPick[], pick: ToolPick): readonly ToolPick[] {
  return picks.some((staged) => staged.id === pick.id)
    ? removeToolPick(picks, pick.id)
    : [...picks, pick];
}

'use client';

import type { FlatRow, TreeItemId } from '../types';

// =====================================================================
// Selection helpers — pure functions over flatRows + state.
//
// Finder/Explorer rules implemented here:
//   - plain click  → replace selection, set anchor = id
//   - meta-click   → toggle id, set anchor = id (clicked row becomes new anchor)
//   - shift-click  → range [anchor..id] (replaces selection)
//   - shift+meta   → union(range [anchor..id], previous selection)
//   - shift+arrows → extend range from anchor through new focused row
//   - mod+a        → select all visible rows
//   - escape       → clear selection (anchor stays — focused stays)
// =====================================================================

export interface SelectionState {
  selected: ReadonlySet<TreeItemId>;
  /** Anchor for shift-range. `null` when nothing has been selected yet. */
  anchor: TreeItemId | null;
  /** Visual cursor — usually equals the last clicked / arrow-moved row. */
  focused: TreeItemId | null;
}

function indexOf(rows: readonly FlatRow<unknown>[], id: TreeItemId | null): number {
  if (id == null) return -1;
  for (let i = 0; i < rows.length; i++) {
    if (rows[i]?.node.id === id) return i;
  }
  return -1;
}

/**
 * Inclusive range of ids between `fromId` and `toId` according to their
 * positions in `rows`. Returns an empty array if either endpoint is not in
 * `rows` (e.g. anchor pointed at a row that got collapsed away).
 */
export function computeRange<T>(
  rows: readonly FlatRow<T>[],
  fromId: TreeItemId | null,
  toId: TreeItemId | null,
): TreeItemId[] {
  if (fromId == null || toId == null) return [];
  const a = indexOf(rows, fromId);
  const b = indexOf(rows, toId);
  if (a < 0 || b < 0) return [];
  const [lo, hi] = a <= b ? [a, b] : [b, a];
  const out: TreeItemId[] = [];
  for (let i = lo; i <= hi; i++) {
    const row = rows[i];
    if (row) out.push(row.node.id);
  }
  return out;
}

/**
 * Click selection — derives next `{selected, anchor, focused}` from a
 * pointer event's modifier keys. `rows` is the current flat view (used
 * for shift-range computation).
 */
export interface ClickModifiers {
  shift: boolean;
  meta: boolean;
}

export function selectionFromClick<T>(
  state: SelectionState,
  rows: readonly FlatRow<T>[],
  id: TreeItemId,
  mods: ClickModifiers,
  multi: boolean,
): SelectionState {
  // Single-selection mode → always collapse to one id.
  if (!multi) {
    return { selected: new Set([id]), anchor: id, focused: id };
  }

  // shift+meta → union of current selection with range from anchor to id.
  if (mods.shift && mods.meta) {
    const anchor = state.anchor ?? state.focused ?? id;
    const range = computeRange(rows, anchor, id);
    const next = new Set(state.selected);
    for (const r of range) next.add(r);
    return { selected: next, anchor: state.anchor ?? id, focused: id };
  }

  // shift-only → replace with range from anchor to id.
  if (mods.shift) {
    const anchor = state.anchor ?? state.focused ?? id;
    const range = computeRange(rows, anchor, id);
    return {
      selected: new Set(range.length > 0 ? range : [id]),
      anchor: state.anchor ?? anchor,
      focused: id,
    };
  }

  // meta-only → toggle id, reset anchor.
  if (mods.meta) {
    const next = new Set(state.selected);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    return { selected: next, anchor: id, focused: id };
  }

  // Plain click → replace selection.
  return { selected: new Set([id]), anchor: id, focused: id };
}

/**
 * Move-focus selection — used by arrow keys. When `extend` is true (shift),
 * recompute the range from anchor through the new focused id. Otherwise
 * collapse selection to the new id and reset anchor.
 */
export function selectionFromMove<T>(
  state: SelectionState,
  rows: readonly FlatRow<T>[],
  nextFocusedId: TreeItemId,
  extend: boolean,
  multi: boolean,
): SelectionState {
  if (!multi || !extend) {
    return { selected: new Set([nextFocusedId]), anchor: nextFocusedId, focused: nextFocusedId };
  }
  const anchor = state.anchor ?? state.focused ?? nextFocusedId;
  const range = computeRange(rows, anchor, nextFocusedId);
  return {
    selected: new Set(range.length > 0 ? range : [nextFocusedId]),
    anchor,
    focused: nextFocusedId,
  };
}

/**
 * Select every visible row (Cmd/Ctrl+A). Anchor is set to the first row
 * so a subsequent shift-click extends from a predictable starting point.
 */
export function selectionSelectAll<T>(
  rows: readonly FlatRow<T>[],
  focused: TreeItemId | null,
): SelectionState {
  if (rows.length === 0) {
    return { selected: new Set(), anchor: null, focused };
  }
  const ids = rows.map((r) => r.node.id);
  const first = ids[0] ?? null;
  return {
    selected: new Set(ids),
    anchor: first,
    focused: focused ?? first,
  };
}

/**
 * Esc behaviour — clear selected items and anchor, but keep focused so the
 * visual cursor stays where the user left it (Finder mimics this).
 */
export function selectionClear(state: SelectionState): SelectionState {
  return { selected: new Set(), anchor: null, focused: state.focused };
}

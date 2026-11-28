'use client';

import type { TreeItemId, TreeMovePosition, TreeNode } from '../types';

// =====================================================================
// Drag-and-drop primitives — pure, framework-agnostic.
//
// @dnd-kit handles the pointer/keyboard sensors and overlay rendering;
// these helpers only translate pointer geometry into a domain-level
// drop position (`before` / `inside` / `after`) and validate whether
// a given drag/drop combo is allowed.
//
// Folder vs leaf semantics:
//   - leaves        → no `inside` zone; row splits into top/bottom halves
//                     for `before` / `after` reorder
//   - folders       → top third = `before`, middle third = `inside`,
//                     bottom third = `after`
// =====================================================================

export interface DropZoneInput {
  /** Pointer Y in viewport coordinates. */
  pointerY: number;
  /** Row bounding box (`getBoundingClientRect()`). */
  rowRect: { top: number; bottom: number; height: number };
  /** Folders accept `inside` drops; leaves only reorder via before/after. */
  isFolder: boolean;
}

/**
 * Translate pointer geometry into a drop position relative to the row.
 *
 * For folders the row is split into three zones (top third / middle /
 * bottom third). For leaves it's split in half (before / after).
 */
export function resolveDropZone(input: DropZoneInput): TreeMovePosition {
  const { pointerY, rowRect, isFolder } = input;
  const offset = pointerY - rowRect.top;
  const ratio = rowRect.height > 0 ? offset / rowRect.height : 0.5;

  if (isFolder) {
    if (ratio < 0.33) return 'before';
    if (ratio > 0.66) return 'after';
    return 'inside';
  }
  return ratio < 0.5 ? 'before' : 'after';
}

// =====================================================================
// canDrop — default validator.
//
// Rejects:
//   1. Dropping a node onto itself.
//   2. Dropping a folder into one of its own descendants (would create
//      a cycle).
//   3. Dropping `inside` a non-folder (defensive — UI already routes
//      these as `before`/`after`, but the API can be called directly).
//
// Consumers can pass their own `canDrop` via `<TreeRoot canDrop={…}>`
// to layer extra rules on top (e.g. read-only branches, type matching).
// =====================================================================

export interface CanDropInput<T> {
  /** Nodes being dragged. */
  source: TreeNode<T>[];
  /** Row under the pointer (`null` = root drop zone). */
  target: TreeNode<T> | null;
  /** Resolved drop position. */
  position: TreeMovePosition;
  /** Tree's id→node lookup, used to walk descendants. */
  getNodeById: (id: TreeItemId) => TreeNode<T> | undefined;
}

export function defaultCanDrop<T>(input: CanDropInput<T>): boolean {
  const { source, target, position } = input;
  if (source.length === 0) return false;
  if (!target) return true; // root drop is always allowed when no other rule rejects.

  // Inside a leaf doesn't make sense.
  if (position === 'inside') {
    const isFolder = Array.isArray(target.children) || !!target.isFolder;
    if (!isFolder) return false;
  }

  for (const node of source) {
    if (node.id === target.id) return false;
    if (isDescendant(node, target.id)) return false;
  }
  return true;
}

/**
 * Walk `root`'s inline children searching for `id`. Cached async children
 * are *not* walked here because the cycle check needs to be cheap and
 * deterministic — a missing cycle in unloaded branches is acceptable
 * (the consumer's `adapter.move` is the final gatekeeper).
 */
function isDescendant<T>(root: TreeNode<T>, id: TreeItemId): boolean {
  if (!Array.isArray(root.children)) return false;
  for (const child of root.children) {
    if (child.id === id) return true;
    if (isDescendant(child, id)) return true;
  }
  return false;
}

// =====================================================================
// DataTransfer mime — used both for in-tree drags and (later) for
// receiving dragged files from the OS. The id payload is the JSON-
// encoded list of `TreeItemId`s.
// =====================================================================

export const TREE_DND_MIME = 'application/x-djangocfg-tree';

/**
 * Sentinel droppable id used by `<TreeEmptyArea>` to claim the
 * "root drop target" slot. `<TreeDndProvider>` recognises this id and
 * maps it to `{ id: null, position: 'inside' }` in `dnd.dropTarget`.
 *
 * Lives in `data/` (not in the component) so both producer and
 * consumer reference one constant instead of duplicating the magic
 * string.
 */
export const TREE_ROOT_DROP_ID = '__tree_root_drop__';

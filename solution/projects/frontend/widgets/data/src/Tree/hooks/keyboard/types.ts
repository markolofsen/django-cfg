'use client';

import type { FlatRow, TreeItemId } from '../../types';

export interface UseTreeKeyboardOptions<T> {
  rows: FlatRow<T>[];
  focusedId: TreeItemId | null;
  enabled?: boolean;
  /**
   * `true` when `selectionMode === 'multiple'` — enables shift-extend on
   * arrow keys, Home / End, and `Cmd/Ctrl+A` select-all. Without it the
   * shift-modifier just moves focus.
   */
  multiSelect?: boolean;
  /**
   * Move focus to `id`. When `extend` is true and multi-select is enabled,
   * the consumer should extend the selection range from anchor through id.
   */
  onFocus: (id: TreeItemId, opts: { extend: boolean }) => void;
  onSelect: (id: TreeItemId) => void;
  onActivate: (id: TreeItemId) => void;
  onExpand: (id: TreeItemId) => void;
  onCollapse: (id: TreeItemId) => void;
  onClearSelection: () => void;
  /** Cmd/Ctrl+A — select all visible rows. Ignored if multiSelect is false. */
  onSelectAll?: () => void;
}

export interface UseTreeKeyboardReturn {
  /** Attach to the tree container. Hotkeys only fire when focus is inside. */
  ref: (instance: HTMLElement | null) => void;
}

/** Reduced state shape passed to action helpers — keeps them pure. */
export interface CurrentRow<T> {
  rows: FlatRow<T>[];
  idx: number;
  current: FlatRow<T> | null;
}

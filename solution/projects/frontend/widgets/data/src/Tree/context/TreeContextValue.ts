'use client';

import type { ClipboardState } from '../data/clipboard';
import type { UseDndReturn } from './dnd';
import type { ResolvedAppearance } from '../data/appearance';
import type { ClickModifiers } from '../data/selection';
import type {
  FlatRow,
  TreeActivateOptions,
  TreeActivationMode,
  TreeAdapter,
  TreeContextMenuItem,
  TreeContextMenuSlot,
  TreeItemId,
  TreeLabels,
  TreeMovePosition,
  TreeNode,
  TreeRowRenderProps,
  TreeRowSlot,
  TreeSelectionMode,
} from '../types';

export interface TreeContextValue<T> {
  // State
  expanded: ReadonlySet<TreeItemId>;
  selected: ReadonlySet<TreeItemId>;
  /** Anchor for shift-range. `null` when nothing has been clicked yet. */
  anchor: TreeItemId | null;
  focused: TreeItemId | null;
  query: string;
  /** Id of the row currently in inline-rename mode (or `null`). */
  renamingId: TreeItemId | null;
  /** Is inline rename allowed by the host? */
  inlineRenameEnabled: boolean;

  /** Tree-local clipboard (cut / copy) — P5. `null` when empty. */
  clipboard: ClipboardState;

  // Flattened render rows (visible items only)
  flatRows: FlatRow<T>[];
  /** Search-matching node ids (subset of all flatRows). */
  matchingIds: ReadonlySet<TreeItemId>;

  // Imperative actions
  expand: (id: TreeItemId) => void;
  collapse: (id: TreeItemId) => void;
  toggle: (id: TreeItemId) => void;
  expandAll: () => void;
  collapseAll: () => void;
  select: (id: TreeItemId) => void;
  setSelectedIds: (ids: TreeItemId[]) => void;
  clearSelection: () => void;
  /**
   * Finder/Explorer-style click selection. Reads modifier keys from the
   * passed event and decides between replace / toggle / range / union.
   */
  clickSelect: (id: TreeItemId, mods: ClickModifiers) => void;
  /**
   * Move-focus with optional range-extend (shift+arrows).
   */
  moveSelect: (id: TreeItemId, opts: { extend: boolean }) => void;
  /** Select every currently visible row (mod+a). */
  selectAll: () => void;
  setFocus: (id: TreeItemId | null) => void;
  setQuery: (q: string) => void;

  /** Put the given ids on Tree's clipboard as `cut`. */
  cutToClipboard: (ids: TreeItemId[]) => void;
  /** Put the given ids on Tree's clipboard as `copy`. */
  copyToClipboard: (ids: TreeItemId[]) => void;
  /**
   * Apply clipboard onto `target` (a row, or `null` for the root). Cut →
   * `adapter.move`; copy → `adapter.copy`. After a successful cut+paste
   * the clipboard is cleared. No-op when clipboard is empty or the
   * matching adapter method is undefined.
   */
  pasteFromClipboard: (
    target: TreeNode<T> | null,
    position?: TreeMovePosition,
  ) => Promise<void>;
  /** Clear the clipboard without pasting. */
  clearClipboard: () => void;

  /** Begin inline rename on the given row. */
  startRename: (id: TreeItemId) => void;
  /** Cancel inline rename without committing. */
  cancelRename: () => void;
  /**
   * Commit inline rename. Tree calls `adapter.rename` and then clears
   * the renaming state. On validation failure surfaces an error via
   * `window.dialog.alert` and keeps the input open.
   */
  commitRename: (id: TreeItemId, nextName: string) => Promise<boolean>;

  refresh: (id: TreeItemId) => Promise<void>;
  refreshAll: () => Promise<void>;
  activate: (node: TreeNode<T>, opts?: TreeActivateOptions) => void;

  // Config / slots
  labels: TreeLabels;
  /** Resolved cosmetic config — never null. */
  appearance: ResolvedAppearance;
  /** Convenience alias for `appearance.indent`. */
  indent: number;
  selectionMode: TreeSelectionMode;
  activationMode: TreeActivationMode;
  enableSearch: boolean;
  showIndentGuides: boolean;
  getItemName: (node: TreeNode<T>) => string;

  renderIcon?: TreeRowSlot<T>;
  renderLabel?: TreeRowSlot<T>;
  renderActions?: TreeRowSlot<T>;
  renderContextMenu?: TreeContextMenuSlot<T>;

  /** CRUD adapter (P2). May be undefined — Tree still renders normally. */
  adapter?: TreeAdapter<T>;
  /**
   * Final, merged declarative menu resolver. Combines built-in adapter
   * actions (filtered by `defaultMenuItems`) with the consumer's
   * `contextMenuActions` resolver, and injects the current
   * `selectedNodes` before delegating.
   */
  resolvedContextMenuActions?: (
    row: TreeRowRenderProps<T>,
  ) => TreeContextMenuItem<T>[] | null | undefined;
  /**
   * Imperative lookup for any node currently known to Tree (root +
   * cached async children).
   */
  getNodeById: (id: TreeItemId) => TreeNode<T> | undefined;

  /**
   * Drag-and-drop state and handlers (P6). `dnd.active` is `false`
   * when the host didn't enable DnD or `adapter.move` is missing — in
   * that case `TreeRow` skips all drag setup.
   */
  dnd: UseDndReturn<T>;
}

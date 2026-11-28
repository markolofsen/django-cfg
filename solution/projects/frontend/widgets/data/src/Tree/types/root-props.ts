'use client';

import type { CSSProperties } from 'react';

import type { TreeAppearance } from '../data/appearance';
import type { TreeActivateOptions, TreeActivationMode } from './activation';
import type {
  TreeAdapter,
  TreeBuiltinAction,
  TreeMovePosition,
} from './adapter';
import type { TreeLabels } from './labels';
import type { TreeLoadChildren } from './loader';
import type { TreeItemId, TreeNode } from './node';
import type { TreeSelectionMode } from './selection';
import type {
  TreeContextMenuActionsResolver,
  TreeContextMenuSlot,
  TreeRowSlot,
} from './slots';

export interface TreeRootProps<T> {
  /** Root nodes. Top-level items are rendered directly (no synthetic root). */
  data: TreeNode<T>[];
  /** Returns the human-readable name for a node (used by search/type-ahead). */
  getItemName: (node: TreeNode<T>) => string;

  /** Async loader for folders without inline `children`. */
  loadChildren?: TreeLoadChildren<T>;

  /** Selection behaviour. Default: `'single'`. */
  selectionMode?: TreeSelectionMode;
  /** Pointer activation behaviour. Default: `'single-click'`. */
  activationMode?: TreeActivationMode;
  /** Initially expanded ids. */
  initialExpandedIds?: TreeItemId[];
  /** Initially selected ids. */
  initialSelectedIds?: TreeItemId[];
  /** Pixels of indent per nesting level. Default: 16. (Shortcut for `appearance.indent`.) */
  indent?: number;
  /** Cosmetic configuration: density, sizes, accent intensity, radius. */
  appearance?: TreeAppearance;

  /** Triggered when selection changes. */
  onSelectionChange?: (selectedIds: TreeItemId[]) => void;
  /** Triggered when expanded set changes. */
  onExpansionChange?: (expandedIds: TreeItemId[]) => void;
  /**
   * Triggered when a leaf is activated (Enter / dblclick / click depending
   * on `activationMode`). Folders never call this — they toggle instead.
   */
  onActivate?: (node: TreeNode<T>, opts: TreeActivateOptions) => void;

  /**
   * Optional predicate. Nodes returning `false` (and their descendants) are
   * not rendered and not searchable. Use this to hide dot-files, system
   * entries, or anything else the consumer wants to filter out.
   */
  filterNode?: (node: TreeNode<T>) => boolean;

  /** Show built-in search input. Default: false. */
  enableSearch?: boolean;
  /** Type printable letters to jump to a matching name. Default: true. */
  enableTypeAhead?: boolean;
  /** Render vertical indent guides under expanded folders. Default: false. */
  showIndentGuides?: boolean;
  /**
   * Allow inline rename. When true, F2 starts an inline `<input>`; the
   * value is committed through `adapter.rename`. Requires `adapter.rename`.
   * Default: false.
   */
  enableInlineRename?: boolean;
  /**
   * Enable Finder/Explorer keyboard shortcuts (delete, rename, duplicate,
   * new file/folder, cut/copy/paste). Bindings only fire when the tree
   * container has focus. Individual shortcuts are still gated by the
   * adapter — `⌘⌫` does nothing if `adapter.remove` is undefined.
   * Default: false.
   */
  enableFinderHotkeys?: boolean;
  /**
   * Enable drag-and-drop reorder + move-into-folder. Requires
   * `adapter.move`. Powered by `@dnd-kit/core` — pointer + keyboard
   * sensors, accessible.
   * Default: false.
   */
  enableDnD?: boolean;
  /**
   * Custom drop validation. Returns `true` to allow, `false` to forbid.
   * The default validator rejects self-drops and cycles (dropping a
   * folder into its own descendant). Use this to add domain rules
   * (read-only branches, type matching, …).
   */
  canDrop?: (ctx: {
    source: TreeNode<T>[];
    target: TreeNode<T> | null;
    position: TreeMovePosition;
  }) => boolean;

  /** Custom row renderer. Falls back to the default <TreeRow />. */
  renderRow?: TreeRowSlot<T>;
  /** Replace default folder/file icon. */
  renderIcon?: TreeRowSlot<T>;
  /** Replace default label rendering. */
  renderLabel?: TreeRowSlot<T>;
  /** Right-side actions slot (per row). */
  renderActions?: TreeRowSlot<T>;
  /** Wrap each row in a context menu (right-click). Receives the row meta + trigger element. */
  renderContextMenu?: TreeContextMenuSlot<T>;
  /**
   * Declarative right-click menu — short-form. Pass `(row) => [items]` and the
   * Tree builds a `<ContextMenu>` for you with sensible defaults. Ignored if
   * `renderContextMenu` is also set. Return `null`/`undefined`/`[]` to skip
   * the menu for that row.
   */
  contextMenuActions?: TreeContextMenuActionsResolver<T>;

  /** Override built-in copy in your locale. */
  labels?: Partial<TreeLabels>;
  /** Persist expanded + (optional) selected ids in localStorage under this key. */
  persistKey?: string;
  /** Persist selection alongside expansion. Default: false. */
  persistSelection?: boolean;

  /**
   * CRUD adapter. When set, Tree builds default context-menu items and
   * Finder hotkeys for every method the adapter defines. Methods that
   * are not provided produce no UI — no greyed-out items.
   */
  adapter?: TreeAdapter<T>;
  /**
   * Which built-in actions to expose in the auto-built context menu. If
   * omitted, every action whose adapter method exists is shown.
   *
   * Pass `[]` to suppress the auto-built menu entirely while keeping the
   * adapter for hotkeys / DnD.
   */
  defaultMenuItems?: TreeBuiltinAction[];

  /**
   * Imperative handle for outer code. The provided ref receives a
   * stable handle to `useTreeActions` once Tree mounts. Lets host
   * components trigger `refresh(id)` / `refreshAll()` from outside
   * Tree (e.g. after a transport-level mutation completes).
   */
  actionsRef?: React.MutableRefObject<TreeActionsHandle | null>;

  className?: string;
  style?: CSSProperties;
}

/** Subset of `useTreeActions()` exposed via `<TreeRoot actionsRef={…}>`. */
export interface TreeActionsHandle {
  refresh: (id: string) => Promise<void>;
  refreshAll: () => Promise<void>;
  expandAll: () => void;
  collapseAll: () => void;
}

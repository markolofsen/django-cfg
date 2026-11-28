'use client';

import type { TreeNode } from './node';

/**
 * Position of a drop / move relative to the target row. `inside` means
 * "drop into this folder"; `before`/`after` are sibling reorder hints.
 */
export type TreeMovePosition = 'before' | 'inside' | 'after';

/**
 * CRUD adapter. Every method is optional — Tree only surfaces built-in
 * menu items / hotkeys whose adapter method is defined. So an
 * inspection-only tree just passes `{}` (or no adapter) and gets no
 * destructive menu actions.
 *
 * Dialogs (`alert` / `confirm` / `prompt`) are taken from `window.dialog`
 * exposed by `<DialogProvider />` in `@djangocfg/ui-core`. The host app
 * is expected to mount that provider once at the layout level — Tree
 * never re-implements its own dialogs.
 */
export interface TreeAdapter<T = unknown> {
  /** Delete the given nodes. Tree calls `window.dialog.confirm` first. */
  remove?: (nodes: TreeNode<T>[]) => Promise<void>;
  /** Inline rename — node + new name (already non-empty, post-validate). */
  rename?: (node: TreeNode<T>, nextName: string) => Promise<void>;
  /** Create a file under `parent` (null → root). Tree prompts for name. */
  createFile?: (parent: TreeNode<T> | null, name: string) => Promise<void>;
  /** Create a folder under `parent` (null → root). Tree prompts for name. */
  createFolder?: (parent: TreeNode<T> | null, name: string) => Promise<void>;
  /** Duplicate the given nodes in-place. */
  duplicate?: (nodes: TreeNode<T>[]) => Promise<void>;
  /** Move nodes (drag-and-drop, cut+paste). */
  move?: (
    nodes: TreeNode<T>[],
    target: TreeNode<T> | null,
    position: TreeMovePosition,
  ) => Promise<void>;
  /** Copy nodes (copy+paste, drop with modifier). */
  copy?: (
    nodes: TreeNode<T>[],
    target: TreeNode<T> | null,
    position: TreeMovePosition,
  ) => Promise<void>;

  /**
   * Optional name validator. Return a non-empty string to surface as an
   * error via `window.dialog.alert`. Return `null` to accept.
   */
  validateName?: (
    name: string,
    ctx: { node?: TreeNode<T>; parent?: TreeNode<T> | null },
  ) => string | null;
}

/**
 * Built-in action ids. Used by `defaultMenuItems` and the internal
 * built-in action registry. Each id maps 1:1 to an adapter method
 * (plus a few selection helpers).
 */
export type TreeBuiltinAction =
  | 'open'
  | 'rename'
  | 'duplicate'
  | 'cut'
  | 'copy'
  | 'paste'
  | 'delete'
  | 'new-file'
  | 'new-folder';

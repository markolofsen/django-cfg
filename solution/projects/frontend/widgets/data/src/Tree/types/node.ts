'use client';

export type TreeItemId = string;

/** A single node in the consumer's tree data. Generic over your payload. */
export interface TreeNode<T = unknown> {
  id: TreeItemId;
  data: T;
  /** Inline children. Omit (and provide a `loadChildren`) for async loading. */
  children?: TreeNode<T>[];
  /**
   * Set to `true` to mark a node as a folder even when its `children` array
   * is empty (e.g. an unloaded async folder). Default: derived from
   * `Array.isArray(children)`.
   */
  isFolder?: boolean;
  /** Disable interaction. */
  disabled?: boolean;
}

/**
 * Internal flat-row representation used by the renderer + keyboard nav.
 * Produced by `flattenTree`; consumed by `TreeRow`, the keyboard hook,
 * and the type-ahead hook.
 */
export interface FlatRow<T> {
  node: TreeNode<T>;
  level: number;
  parentId: TreeItemId | null;
  isFolder: boolean;
  isExpanded: boolean;
  isLoading: boolean;
  hasError: boolean;
  /** 1-based position among visible siblings (for `aria-posinset`). */
  posInSet: number;
  /** Count of visible siblings sharing this row's parent (for `aria-setsize`). */
  setSize: number;
}

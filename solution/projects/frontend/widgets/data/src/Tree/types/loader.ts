'use client';

import type { TreeNode } from './node';

/**
 * Async loader: called the first time a folder is expanded with no inline
 * `children`. Result is cached; concurrent expansions are de-duplicated.
 */
export type TreeLoadChildren<T> = (node: TreeNode<T>) => Promise<TreeNode<T>[]>;

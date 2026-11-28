'use client';

import type { TreeItemId, TreeNode } from '../types';

export type ChildEntryStatus = 'idle' | 'loading' | 'loaded' | 'error';

export interface ChildEntry<T> {
  status: ChildEntryStatus;
  children: TreeNode<T>[];
  error?: string;
}

export type ChildCache<T> = Map<TreeItemId, ChildEntry<T>>;

export const createChildCache = <T>(): ChildCache<T> => new Map();

export const getEntry = <T>(
  cache: ChildCache<T>,
  id: TreeItemId,
): ChildEntry<T> | undefined => cache.get(id);

/**
 * Resolve a node's children for the current render.
 *
 * - If the node carries inline `children`, those win (no async fetch).
 * - Otherwise we look in the cache.
 *
 * Returns `null` when nothing is loaded yet (caller may show a skeleton).
 */
export const resolveChildren = <T>(
  cache: ChildCache<T>,
  node: TreeNode<T>,
): { children: TreeNode<T>[] | null; status: ChildEntryStatus; error?: string } => {
  if (Array.isArray(node.children)) {
    return { children: node.children, status: 'loaded' };
  }
  const entry = cache.get(node.id);
  if (!entry) return { children: null, status: 'idle' };
  if (entry.status === 'loaded') {
    return { children: entry.children, status: 'loaded' };
  }
  return { children: null, status: entry.status, error: entry.error };
};

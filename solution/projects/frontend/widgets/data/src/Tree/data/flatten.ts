'use client';

import type { FlatRow, TreeItemId, TreeNode } from '../types';
import { resolveChildren, type ChildCache } from './childCache';

export interface FlattenInput<T> {
  roots: TreeNode<T>[];
  expandedIds: ReadonlySet<TreeItemId>;
  cache: ChildCache<T>;
  /** Optional predicate. Nodes returning `false` (and their descendants) are excluded. */
  filterNode?: (node: TreeNode<T>) => boolean;
}

const isNodeFolder = <T>(node: TreeNode<T>): boolean => {
  if (typeof node.isFolder === 'boolean') return node.isFolder;
  return Array.isArray(node.children);
};

/**
 * Walk the tree top-to-bottom and produce a flat list of visible rows.
 *
 * Visibility rule: a child row appears only when every ancestor is in
 * `expandedIds`. The output is ordered exactly as it should render,
 * which keeps keyboard navigation (next/prev row) trivial.
 */
export function flattenTree<T>({
  roots,
  expandedIds,
  cache,
  filterNode,
}: FlattenInput<T>): FlatRow<T>[] {
  const out: FlatRow<T>[] = [];

  const walk = (nodes: TreeNode<T>[], level: number, parentId: TreeItemId | null) => {
    // Visible siblings only — `aria-setsize`/`posinset` must ignore filtered nodes.
    const visible = filterNode ? nodes.filter(filterNode) : nodes;
    const setSize = visible.length;

    visible.forEach((node, index) => {
      const isFolder = isNodeFolder(node);
      const isExpanded = expandedIds.has(node.id);
      const resolved = isFolder
        ? resolveChildren(cache, node)
        : { children: [], status: 'loaded' as const };

      out.push({
        node,
        level,
        parentId,
        isFolder,
        isExpanded,
        isLoading: resolved.status === 'loading',
        hasError: resolved.status === 'error',
        posInSet: index + 1,
        setSize,
      });

      if (isFolder && isExpanded && resolved.children) {
        walk(resolved.children, level + 1, node.id);
      }
    });
  };

  walk(roots, 0, null);
  return out;
}

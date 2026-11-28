'use client';

import type { ChildCache } from '../../data/childCache';
import type { TreeItemId, TreeNode } from '../../types';

/**
 * Walk `roots` + cached async children and push every *folder* id into
 * `out`. Used by `expandAll`.
 *
 * Leaves are intentionally not collected — expanding a leaf is a no-op.
 */
export function collectAllFolderIds<T>(
  roots: TreeNode<T>[],
  cache: ChildCache<T>,
  out: TreeItemId[],
): void {
  for (const node of roots) {
    if (Array.isArray(node.children)) {
      out.push(node.id);
      collectAllFolderIds(node.children, cache, out);
    } else if (node.isFolder) {
      out.push(node.id);
      const entry = cache.get(node.id);
      if (entry?.children) collectAllFolderIds(entry.children, cache, out);
    }
  }
}

'use client';

import { useCallback, useEffect, useMemo, useRef } from 'react';

import { createChildCache, type ChildCache } from '../../data/childCache';
import type {
  TreeItemId,
  TreeLoadChildren,
  TreeNode,
} from '../../types';
import { collectAllFolderIds } from './collect-ids';

export interface UseAsyncChildrenOptions<T> {
  data: TreeNode<T>[];
  loadChildren?: TreeLoadChildren<T>;
  /** Current set of expanded ids — controls which async fetches fire. */
  expanded: ReadonlySet<TreeItemId>;
  /** Bumps every time the cache mutates — invalidates downstream memos. */
  cacheTick: number;
  /** Dispatch into the reducer (used to bump `cacheTick`). */
  bumpCacheTick: () => void;
}

export interface UseAsyncChildrenReturn<T> {
  /** Live async-children cache (mutable ref, not React state). */
  cache: ChildCache<T>;
  /** Id → node lookup across the root tree + cached async children. */
  nodeById: Map<TreeItemId, TreeNode<T>>;
  /** Fetch a single folder's children (deduped, idempotent). */
  fetchChildren: (node: TreeNode<T>) => Promise<void> | void;
  /** Drop one node's cache entry and refetch. */
  refresh: (id: TreeItemId) => Promise<void>;
  /** Clear the entire cache and refetch every currently-expanded folder. */
  refreshAll: () => Promise<void>;
  /** Collect every folder id known to Tree (root + cached). For `expandAll`. */
  collectFolderIds: () => TreeItemId[];
}

/**
 * Manage async children: a long-lived cache (in a ref), dedup-ed
 * `loadChildren` calls, and a `nodeById` map that walks both inline
 * children and cached async ones. The cache lives outside reducer state
 * because mutating a Map per render is cheaper than spreading it; we
 * trigger downstream re-renders via the `cacheTick` counter.
 */
export function useAsyncChildren<T>({
  data,
  loadChildren,
  expanded,
  cacheTick,
  bumpCacheTick,
}: UseAsyncChildrenOptions<T>): UseAsyncChildrenReturn<T> {
  // The cache survives provider re-renders and async work.
  const cacheRef = useRef<ChildCache<T>>(createChildCache<T>());
  const inflightRef = useRef<Map<TreeItemId, Promise<void>>>(new Map());

  const fetchChildren = useCallback(
    async (node: TreeNode<T>) => {
      if (!loadChildren) return;
      if (Array.isArray(node.children)) return;
      const existing = cacheRef.current.get(node.id);
      if (existing?.status === 'loaded' || existing?.status === 'loading') return;
      const inflight = inflightRef.current.get(node.id);
      if (inflight) return inflight;

      cacheRef.current.set(node.id, { status: 'loading', children: [] });
      bumpCacheTick();

      const promise = (async () => {
        try {
          const children = await loadChildren(node);
          cacheRef.current.set(node.id, { status: 'loaded', children });
        } catch (err) {
          cacheRef.current.set(node.id, {
            status: 'error',
            children: [],
            error: err instanceof Error ? err.message : String(err),
          });
        } finally {
          inflightRef.current.delete(node.id);
          bumpCacheTick();
        }
      })();

      inflightRef.current.set(node.id, promise);
      return promise;
    },
    [loadChildren, bumpCacheTick],
  );

  // Build a quick id → node map across roots + cached async children.
  // Re-runs whenever the cache mutates (cacheTick) or `data` changes.
  const nodeById = useMemo(() => {
    const map = new Map<TreeItemId, TreeNode<T>>();
    const walk = (nodes: TreeNode<T>[]) => {
      for (const n of nodes) {
        map.set(n.id, n);
        if (Array.isArray(n.children)) walk(n.children);
        else {
          const entry = cacheRef.current.get(n.id);
          if (entry?.children) walk(entry.children);
        }
      }
    };
    walk(data);
    return map;
    // `cacheTick` reads as unnecessary because the walk reaches the cache
    // through `cacheRef.current`, which the linter cannot track. It is the only
    // invalidation signal the cache has: drop it and `nodeById` keeps the map
    // built before the async load, so loaded children stay invisible.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, cacheTick]);

  // Auto-fetch every expanded folder that isn't already in cache. Cheap
  // — `fetchChildren` short-circuits when cached or already inflight.
  useEffect(() => {
    if (!loadChildren) return;
    for (const id of expanded) {
      const node = nodeById.get(id);
      if (!node) continue;
      void fetchChildren(node);
    }
  }, [loadChildren, expanded, cacheTick, nodeById, fetchChildren]);

  const refresh = useCallback(
    async (id: TreeItemId) => {
      const node = nodeById.get(id);
      if (!node || !loadChildren) return;
      cacheRef.current.delete(id);
      bumpCacheTick();
      await fetchChildren(node);
    },
    [nodeById, loadChildren, fetchChildren, bumpCacheTick],
  );

  const refreshAll = useCallback(async () => {
    cacheRef.current.clear();
    bumpCacheTick();
    if (!loadChildren) return;
    await Promise.all(
      [...expanded].map((id) => {
        const node = nodeById.get(id);
        return node ? fetchChildren(node) : undefined;
      }),
    );
  }, [loadChildren, expanded, nodeById, fetchChildren, bumpCacheTick]);

  const collectFolderIds = useCallback(() => {
    const ids: TreeItemId[] = [];
    collectAllFolderIds(data, cacheRef.current, ids);
    return ids;
  }, [data]);

  return {
    cache: cacheRef.current,
    nodeById,
    fetchChildren,
    refresh,
    refreshAll,
    collectFolderIds,
  };
}

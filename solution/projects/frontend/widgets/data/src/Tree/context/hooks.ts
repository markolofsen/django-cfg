'use client';

import { useCallback, useMemo } from 'react';

import type { TreeItemId } from '../types';
import { useTreeContext } from './TreeContext';

export function useTreeLabels() {
  return useTreeContext().labels;
}

export function useTreeRows<T>() {
  return useTreeContext<T>().flatRows;
}

export function useTreeSelection<T>() {
  const ctx = useTreeContext<T>();
  const selectedIds = useMemo(() => [...ctx.selected], [ctx.selected]);
  const isSelected = useCallback(
    (id: TreeItemId) => ctx.selected.has(id),
    [ctx.selected],
  );
  return useMemo(
    () => ({
      selectedIds,
      anchor: ctx.anchor,
      select: ctx.select,
      setSelectedIds: ctx.setSelectedIds,
      clear: ctx.clearSelection,
      clickSelect: ctx.clickSelect,
      moveSelect: ctx.moveSelect,
      selectAll: ctx.selectAll,
      isSelected,
    }),
    [
      selectedIds,
      ctx.anchor,
      ctx.select,
      ctx.setSelectedIds,
      ctx.clearSelection,
      ctx.clickSelect,
      ctx.moveSelect,
      ctx.selectAll,
      isSelected,
    ],
  );
}

export function useTreeExpansion<T>() {
  const ctx = useTreeContext<T>();
  const expandedIds = useMemo(() => [...ctx.expanded], [ctx.expanded]);
  const isExpanded = useCallback(
    (id: TreeItemId) => ctx.expanded.has(id),
    [ctx.expanded],
  );
  return useMemo(
    () => ({
      expandedIds,
      expand: ctx.expand,
      collapse: ctx.collapse,
      toggle: ctx.toggle,
      expandAll: ctx.expandAll,
      collapseAll: ctx.collapseAll,
      isExpanded,
    }),
    [
      expandedIds,
      ctx.expand,
      ctx.collapse,
      ctx.toggle,
      ctx.expandAll,
      ctx.collapseAll,
      isExpanded,
    ],
  );
}

export function useTreeFocus<T>() {
  const ctx = useTreeContext<T>();
  return useMemo(
    () => ({ focusedId: ctx.focused, setFocus: ctx.setFocus }),
    [ctx.focused, ctx.setFocus],
  );
}

export function useTreeSearch<T>() {
  const ctx = useTreeContext<T>();
  return useMemo(
    () => ({
      isOpen: ctx.enableSearch,
      query: ctx.query,
      setQuery: ctx.setQuery,
      matchingIds: ctx.matchingIds,
      matchCount: ctx.matchingIds.size,
    }),
    [ctx.enableSearch, ctx.query, ctx.setQuery, ctx.matchingIds],
  );
}

export function useTreeDnd<T>() {
  const ctx = useTreeContext<T>();
  return ctx.dnd;
}

export function useTreeClipboard<T>() {
  const ctx = useTreeContext<T>();
  const isCut = useCallback(
    (id: TreeItemId) => ctx.clipboard?.kind === 'cut' && ctx.clipboard.ids.includes(id),
    [ctx.clipboard],
  );
  return useMemo(
    () => ({
      clipboard: ctx.clipboard,
      isCut,
      cut: ctx.cutToClipboard,
      copy: ctx.copyToClipboard,
      paste: ctx.pasteFromClipboard,
      clear: ctx.clearClipboard,
    }),
    [
      ctx.clipboard,
      isCut,
      ctx.cutToClipboard,
      ctx.copyToClipboard,
      ctx.pasteFromClipboard,
      ctx.clearClipboard,
    ],
  );
}

export function useTreeRename<T>() {
  const ctx = useTreeContext<T>();
  return useMemo(
    () => ({
      /** True when the host allowed inline rename AND the adapter exposes `rename`. */
      enabled: ctx.inlineRenameEnabled,
      /** Currently renaming id, or `null`. */
      renamingId: ctx.renamingId,
      startRename: ctx.startRename,
      cancelRename: ctx.cancelRename,
      commitRename: ctx.commitRename,
    }),
    [
      ctx.inlineRenameEnabled,
      ctx.renamingId,
      ctx.startRename,
      ctx.cancelRename,
      ctx.commitRename,
    ],
  );
}

export function useTreeActions<T>() {
  const ctx = useTreeContext<T>();
  return useMemo(
    () => ({
      expand: ctx.expand,
      collapse: ctx.collapse,
      toggle: ctx.toggle,
      expandAll: ctx.expandAll,
      collapseAll: ctx.collapseAll,
      refresh: ctx.refresh,
      refreshAll: ctx.refreshAll,
      activate: ctx.activate,
    }),
    [
      ctx.expand,
      ctx.collapse,
      ctx.toggle,
      ctx.expandAll,
      ctx.collapseAll,
      ctx.refresh,
      ctx.refreshAll,
      ctx.activate,
    ],
  );
}

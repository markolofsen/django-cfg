'use client';

import * as React from 'react';
import { createContext, useCallback, useMemo, useReducer, useRef } from 'react';

import { flattenTree } from '../data/flatten';
import { loadTreeState } from '../data/persist';
import { resolveAppearance } from '../data/appearance';
import {
  DEFAULT_TREE_LABELS,
  type FlatRow,
  type TreeActivateOptions,
  type TreeContextMenuSlot,
  type TreeItemId,
  type TreeLabels,
  type TreeNode,
  type TreeRootProps,
} from '../types';

import { reducer, createInitialState } from './state';
import { useAsyncChildren } from './async-children';
import { useExpansion } from './expansion';
import { useSelection } from './selection';
import { useRename } from './rename';
import { useClipboard } from './clipboard';
import { useResolvedMenu, renderItemsAsContextMenu, tidyMenuItems } from './menu';
import { useDnd } from './dnd';
import { usePersistSync } from './persist';
import type { TreeContextValue } from './TreeContextValue';

// Re-exported from this module: the value interface (so consumers
// continue to `import type { TreeContextValue }` from `./context`).
export type { TreeContextValue } from './TreeContextValue';

/**
 * Internal context object. Exported so `TreeRoot` can wrap it with an
 * override-provider that injects a slot-form `renderContextMenu`
 * derived from the declarative resolver. Consumers should use
 * `useTreeContext()` instead of touching this directly.
 */
export const TreeContext = createContext<TreeContextValue<unknown> | null>(null);

export function useTreeContext<T>(): TreeContextValue<T> {
  const ctx = React.useContext(TreeContext);
  if (!ctx) {
    throw new Error('useTreeContext must be used inside <TreeProvider>');
  }
  return ctx as TreeContextValue<T>;
}

// =====================================================================
// Provider — thin assembly. The real work lives in:
//
//   state/           reducer + initial state
//   async-children/  child cache, nodeById, fetchChildren, refresh, refreshAll
//   expansion/       expand / collapse / toggle / expandAll / collapseAll
//   selection/       click / move / select-all + plain select / clear
//   rename/          start / cancel / commit
//   clipboard/       cut / copy / paste / clear
//   menu/            built-in actions registry + merged declarative resolver
//   persist/         localStorage + onSelectionChange/onExpansionChange
//
// This file only stitches them together and shapes the final
// `TreeContextValue`. If a feature grows, add a folder above — don't
// extend this file.
// =====================================================================

export interface TreeProviderProps<T>
  extends Pick<
    TreeRootProps<T>,
    | 'data'
    | 'getItemName'
    | 'loadChildren'
    | 'selectionMode'
    | 'activationMode'
    | 'initialExpandedIds'
    | 'initialSelectedIds'
    | 'indent'
    | 'appearance'
    | 'onSelectionChange'
    | 'onExpansionChange'
    | 'onActivate'
    | 'filterNode'
    | 'enableSearch'
    | 'showIndentGuides'
    | 'renderIcon'
    | 'renderLabel'
    | 'renderActions'
    | 'renderContextMenu'
    | 'contextMenuActions'
    | 'labels'
    | 'persistKey'
    | 'persistSelection'
    | 'adapter'
    | 'defaultMenuItems'
    | 'enableInlineRename'
    | 'enableDnD'
    | 'canDrop'
  > {
  children: React.ReactNode;
}

export function TreeProvider<T>(props: TreeProviderProps<T>) {
  const {
    data,
    getItemName,
    loadChildren,
    selectionMode = 'single',
    activationMode = 'single-click',
    initialExpandedIds,
    initialSelectedIds,
    indent,
    appearance,
    onSelectionChange,
    onExpansionChange,
    onActivate,
    filterNode,
    enableSearch = false,
    showIndentGuides = false,
    renderIcon,
    renderLabel,
    renderActions,
    renderContextMenu,
    contextMenuActions,
    labels: labelsOverride,
    persistKey,
    persistSelection = false,
    adapter,
    defaultMenuItems,
    enableInlineRename = false,
    enableDnD = false,
    canDrop,
    children,
  } = props;

  // ---- Stable config ------------------------------------------------

  const labels = useMemo<TreeLabels>(
    () => ({ ...DEFAULT_TREE_LABELS, ...labelsOverride }),
    [labelsOverride],
  );

  const resolvedAppearance = useMemo(
    () => resolveAppearance(appearance, indent),
    [appearance, indent],
  );

  // ---- Reducer ------------------------------------------------------

  const persisted = useMemo(
    () => (persistKey ? loadTreeState(persistKey) : null),
    [persistKey],
  );

  const [state, dispatch] = useReducer(reducer, undefined, () =>
    createInitialState({
      persisted,
      initialExpandedIds,
      initialSelectedIds,
      persistSelection,
    }),
  );

  const bumpCacheTick = useCallback(() => dispatch({ type: 'cache-tick' }), []);

  // ---- Async children (cache + nodeById + refresh) ------------------

  const {
    nodeById,
    refresh,
    refreshAll,
    collectFolderIds,
    cache,
  } = useAsyncChildren<T>({
    data,
    loadChildren,
    expanded: state.expanded,
    cacheTick: state.cacheTick,
    bumpCacheTick,
  });

  // ---- Flat rows (depend on cache via cacheTick) --------------------

  const flatRows = useMemo<FlatRow<T>[]>(
    () =>
      flattenTree<T>({
        roots: data,
        expandedIds: state.expanded,
        cache,
        filterNode,
      }),
    // `state.cacheTick` reads as unnecessary because `cache` is a stable
    // ref-backed Map whose identity never changes when it mutates. It is the
    // only invalidation signal: drop it and rows for async-loaded children are
    // never flattened, so an expanded folder stays visually empty.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [data, state.expanded, state.cacheTick, cache, filterNode],
  );

  const matchingIds = useMemo(() => {
    const set = new Set<TreeItemId>();
    if (!enableSearch || state.query.trim() === '') return set;
    const q = state.query.trim().toLowerCase();
    for (const row of flatRows) {
      if (getItemName(row.node).toLowerCase().includes(q)) {
        set.add(row.node.id);
      }
    }
    return set;
  }, [enableSearch, state.query, flatRows, getItemName]);

  // ---- Feature hooks ------------------------------------------------

  const expansion = useExpansion({ dispatch, collectFolderIds });
  const selection = useSelection<T>({
    dispatch,
    selectionMode,
    flatRows,
    selected: state.selected,
    anchor: state.anchor,
    focused: state.focused,
  });
  const rename = useRename<T>({
    dispatch,
    adapter,
    enableInlineRename,
    nodeById,
    getItemName,
    labels,
  });
  const clipboard = useClipboard<T>({
    dispatch,
    clipboard: state.clipboard,
    adapter,
    nodeById,
    labels,
  });
  const dnd = useDnd<T>({
    enabled: enableDnD,
    adapter,
    nodeById,
    selected: state.selected,
    labels,
    canDrop,
  });

  // ---- Activation ---------------------------------------------------

  const onActivateRef = useRef(onActivate);
  onActivateRef.current = onActivate;
  const activate = useCallback(
    (node: TreeNode<T>, opts: TreeActivateOptions = { preview: false }) =>
      onActivateRef.current?.(node, opts),
    [],
  );

  const setQuery = useCallback(
    (q: string) => dispatch({ type: 'set-query', q }),
    [],
  );

  // ---- Persist + notify callbacks -----------------------------------

  usePersistSync({
    expanded: state.expanded,
    selected: state.selected,
    persistKey,
    persistSelection,
    onSelectionChange,
    onExpansionChange,
  });

  // ---- Resolved context-menu resolver -------------------------------

  const resolvedContextMenuActions = useResolvedMenu<T>({
    adapter,
    contextMenuActions,
    defaultMenuItems,
    labels,
    selected: state.selected,
    clipboard: state.clipboard,
    nodeById,
    getItemName,
    enableInlineRename,
    startRename: rename.startRename,
    cutToClipboard: clipboard.cutToClipboard,
    copyToClipboard: clipboard.copyToClipboard,
    pasteFromClipboard: clipboard.pasteFromClipboard,
  });

  // Translate the declarative resolver into a slot-form
  // `renderContextMenu` so <TreeRow> doesn't need to know about it.
  // Explicit slot prop wins (escape-hatch for full custom menus).
  const finalRenderContextMenu = useMemo<TreeContextMenuSlot<T> | undefined>(
    () => {
      if (renderContextMenu) return renderContextMenu;
      const resolve = resolvedContextMenuActions;
      if (!resolve) return undefined;
      return (rowProps, trigger) => {
        const items = resolve(rowProps);
        const cleaned = items ? tidyMenuItems(items) : null;
        if (!cleaned || cleaned.length === 0) return trigger;
        return renderItemsAsContextMenu(rowProps, cleaned, trigger);
      };
    },
    [renderContextMenu, resolvedContextMenuActions],
  );

  // ---- Final value --------------------------------------------------

  const value = useMemo<TreeContextValue<T>>(
    () => ({
      // state
      expanded: state.expanded,
      selected: state.selected,
      anchor: state.anchor,
      focused: state.focused,
      query: state.query,
      renamingId: state.renaming,
      inlineRenameEnabled: rename.enabled,
      clipboard: state.clipboard,
      flatRows,
      matchingIds,

      // expansion
      ...expansion,

      // selection (note: `select` is from selection hook; expansion exports no `select`)
      ...selection,

      setQuery,

      // clipboard
      ...clipboard,

      // rename
      startRename: rename.startRename,
      cancelRename: rename.cancelRename,
      commitRename: rename.commitRename,

      // async
      refresh,
      refreshAll,
      activate,

      // config
      labels,
      appearance: resolvedAppearance,
      indent: resolvedAppearance.indent,
      selectionMode,
      activationMode,
      enableSearch,
      showIndentGuides,
      getItemName,

      // slots
      renderIcon,
      renderLabel,
      renderActions,
      renderContextMenu: finalRenderContextMenu,

      adapter,
      resolvedContextMenuActions,
      getNodeById: (id: TreeItemId) => nodeById.get(id),
      dnd,
    }),
    [
      state.expanded,
      state.selected,
      state.anchor,
      state.focused,
      state.query,
      state.renaming,
      state.clipboard,
      rename.enabled,
      rename.startRename,
      rename.cancelRename,
      rename.commitRename,
      flatRows,
      matchingIds,
      expansion,
      selection,
      setQuery,
      clipboard,
      refresh,
      refreshAll,
      activate,
      labels,
      resolvedAppearance,
      selectionMode,
      activationMode,
      enableSearch,
      showIndentGuides,
      getItemName,
      renderIcon,
      renderLabel,
      renderActions,
      finalRenderContextMenu,
      adapter,
      resolvedContextMenuActions,
      nodeById,
      dnd,
    ],
  );

  return (
    <TreeContext.Provider value={value as TreeContextValue<unknown>}>
      {children}
    </TreeContext.Provider>
  );
}

// Re-export internal types referenced by hook consumers.
export type { ChildCache, ChildEntry } from '../data/childCache';

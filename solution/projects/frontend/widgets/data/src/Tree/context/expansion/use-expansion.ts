'use client';

import { useCallback } from 'react';

import type { Action } from '../state';
import type { TreeItemId } from '../../types';

export interface UseExpansionOptions {
  dispatch: React.Dispatch<Action>;
  /** Build the "all folder ids" list — usually wired to `useAsyncChildren`. */
  collectFolderIds: () => TreeItemId[];
}

export interface UseExpansionReturn {
  expand: (id: TreeItemId) => void;
  collapse: (id: TreeItemId) => void;
  toggle: (id: TreeItemId) => void;
  expandAll: () => void;
  collapseAll: () => void;
}

/**
 * Thin action wrappers around the reducer's expansion actions, plus
 * `expandAll` / `collapseAll`. `expandAll` walks roots and cached async
 * children so partially-loaded trees expand everything they currently
 * know about.
 */
export function useExpansion({
  dispatch,
  collectFolderIds,
}: UseExpansionOptions): UseExpansionReturn {
  const expand = useCallback(
    (id: TreeItemId) => dispatch({ type: 'expand', id }),
    [dispatch],
  );
  const collapse = useCallback(
    (id: TreeItemId) => dispatch({ type: 'collapse', id }),
    [dispatch],
  );
  const toggle = useCallback(
    (id: TreeItemId) => dispatch({ type: 'toggle', id }),
    [dispatch],
  );

  const expandAll = useCallback(() => {
    dispatch({ type: 'set-expanded', ids: collectFolderIds() });
  }, [dispatch, collectFolderIds]);

  const collapseAll = useCallback(
    () => dispatch({ type: 'set-expanded', ids: [] }),
    [dispatch],
  );

  return { expand, collapse, toggle, expandAll, collapseAll };
}

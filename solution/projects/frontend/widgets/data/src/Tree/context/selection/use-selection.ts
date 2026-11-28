'use client';

import { useCallback, useRef } from 'react';

import {
  selectionFromClick,
  selectionFromMove,
  selectionSelectAll,
  type ClickModifiers,
} from '../../data/selection';
import type {
  FlatRow,
  TreeItemId,
  TreeSelectionMode,
} from '../../types';
import type { Action } from '../state';

export interface UseSelectionOptions<T> {
  dispatch: React.Dispatch<Action>;
  selectionMode: TreeSelectionMode;
  /** Current visible rows — fed in each render, latched into a ref. */
  flatRows: FlatRow<T>[];
  /** Current selection snapshot (latched into a ref alongside `flatRows`). */
  selected: ReadonlySet<TreeItemId>;
  anchor: TreeItemId | null;
  focused: TreeItemId | null;
}

export interface UseSelectionReturn {
  select: (id: TreeItemId) => void;
  setSelectedIds: (ids: TreeItemId[]) => void;
  clearSelection: () => void;
  clickSelect: (id: TreeItemId, mods: ClickModifiers) => void;
  moveSelect: (id: TreeItemId, opts: { extend: boolean }) => void;
  selectAll: () => void;
  setFocus: (id: TreeItemId | null) => void;
}

/**
 * Finder/Explorer-style selection actions. Reads the *current* rows /
 * selection from refs latched per-render, so the returned callbacks
 * stay stable across renders (which matters for `react-hotkeys-hook`
 * and for memoised TreeRow children).
 */
export function useSelection<T>({
  dispatch,
  selectionMode,
  flatRows,
  selected,
  anchor,
  focused,
}: UseSelectionOptions<T>): UseSelectionReturn {
  // Latch the snapshot the callbacks read from.
  const flatRowsRef = useRef<FlatRow<T>[]>(flatRows);
  flatRowsRef.current = flatRows;
  const selectionRef = useRef({ selected, anchor, focused });
  selectionRef.current = { selected, anchor, focused };

  const select = useCallback(
    (id: TreeItemId) => dispatch({ type: 'select', id, mode: selectionMode }),
    [dispatch, selectionMode],
  );
  const setSelectedIds = useCallback(
    (ids: TreeItemId[]) => dispatch({ type: 'select-many', ids }),
    [dispatch],
  );
  const clearSelection = useCallback(
    () => dispatch({ type: 'clear-selection' }),
    [dispatch],
  );
  const setFocus = useCallback(
    (id: TreeItemId | null) => dispatch({ type: 'focus', id }),
    [dispatch],
  );

  const clickSelect = useCallback(
    (id: TreeItemId, mods: ClickModifiers) => {
      if (selectionMode === 'none') return;
      if (selectionMode === 'single') {
        dispatch({ type: 'select', id, mode: 'single' });
        return;
      }
      const next = selectionFromClick(
        selectionRef.current,
        flatRowsRef.current,
        id,
        mods,
        true,
      );
      dispatch({
        type: 'selection-replace',
        selected: [...next.selected],
        anchor: next.anchor,
        focused: next.focused,
      });
    },
    [dispatch, selectionMode],
  );

  const moveSelect = useCallback(
    (id: TreeItemId, opts: { extend: boolean }) => {
      if (selectionMode !== 'multiple' || !opts.extend) {
        dispatch({ type: 'focus', id });
        return;
      }
      const next = selectionFromMove(
        selectionRef.current,
        flatRowsRef.current,
        id,
        true,
        true,
      );
      dispatch({
        type: 'selection-replace',
        selected: [...next.selected],
        anchor: next.anchor,
        focused: next.focused,
      });
    },
    [dispatch, selectionMode],
  );

  const selectAll = useCallback(() => {
    if (selectionMode !== 'multiple') return;
    const next = selectionSelectAll(
      flatRowsRef.current,
      selectionRef.current.focused,
    );
    dispatch({
      type: 'selection-replace',
      selected: [...next.selected],
      anchor: next.anchor,
      focused: next.focused,
    });
  }, [dispatch, selectionMode]);

  return {
    select,
    setSelectedIds,
    clearSelection,
    clickSelect,
    moveSelect,
    selectAll,
    setFocus,
  };
}

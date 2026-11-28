'use client';

import { useCallback, useRef } from 'react';

import { getDialog } from '@djangocfg/ui-core/lib/dialog-service';

import type { ClipboardState } from '../../data/clipboard';
import type {
  TreeAdapter,
  TreeItemId,
  TreeLabels,
  TreeMovePosition,
  TreeNode,
} from '../../types';
import type { Action } from '../state';

export interface UseClipboardOptions<T> {
  dispatch: React.Dispatch<Action>;
  /** Current clipboard snapshot — latched into a ref for async paste. */
  clipboard: ClipboardState;
  adapter?: TreeAdapter<T>;
  nodeById: Map<TreeItemId, TreeNode<T>>;
  labels: TreeLabels;
}

export interface UseClipboardReturn<T> {
  cutToClipboard: (ids: TreeItemId[]) => void;
  copyToClipboard: (ids: TreeItemId[]) => void;
  /** Apply clipboard to `target` (a row, or `null` = root). */
  pasteFromClipboard: (
    target: TreeNode<T> | null,
    position?: TreeMovePosition,
  ) => Promise<void>;
  clearClipboard: () => void;
}

/**
 * Tree-local clipboard. Cut + paste dispatches `adapter.move`, copy +
 * paste dispatches `adapter.copy`. Errors are surfaced through
 * `window.dialog.alert` so they don't get swallowed silently.
 */
export function useClipboard<T>({
  dispatch,
  clipboard,
  adapter,
  nodeById,
  labels,
}: UseClipboardOptions<T>): UseClipboardReturn<T> {
  const clipboardRef = useRef(clipboard);
  clipboardRef.current = clipboard;

  const cutToClipboard = useCallback(
    (ids: TreeItemId[]) => {
      if (ids.length === 0) return;
      dispatch({ type: 'clipboard-set', payload: { kind: 'cut', ids } });
    },
    [dispatch],
  );

  const copyToClipboard = useCallback(
    (ids: TreeItemId[]) => {
      if (ids.length === 0) return;
      dispatch({ type: 'clipboard-set', payload: { kind: 'copy', ids } });
    },
    [dispatch],
  );

  const clearClipboard = useCallback(
    () => dispatch({ type: 'clipboard-set', payload: null }),
    [dispatch],
  );

  const pasteFromClipboard = useCallback(
    async (
      target: TreeNode<T> | null,
      position: TreeMovePosition = 'inside',
    ) => {
      const cb = clipboardRef.current;
      if (!cb || cb.ids.length === 0) return;
      if (!adapter) return;
      const nodes = cb.ids
        .map((id) => nodeById.get(id))
        .filter((n): n is TreeNode<T> => !!n);
      if (nodes.length === 0) {
        dispatch({ type: 'clipboard-set', payload: null });
        return;
      }
      try {
        if (cb.kind === 'cut') {
          if (!adapter.move) return;
          await adapter.move(nodes, target, position);
          // Cut + paste consumes the clipboard. Copy + paste retains it.
          dispatch({ type: 'clipboard-set', payload: null });
        } else {
          if (!adapter.copy) return;
          await adapter.copy(nodes, target, position);
        }
      } catch (e) {
        const dialog = getDialog();
        await dialog?.alert({
          title: labels.error,
          message: e instanceof Error ? e.message : String(e),
        });
      }
    },
    [dispatch, adapter, nodeById, labels],
  );

  return {
    cutToClipboard,
    copyToClipboard,
    pasteFromClipboard,
    clearClipboard,
  };
}

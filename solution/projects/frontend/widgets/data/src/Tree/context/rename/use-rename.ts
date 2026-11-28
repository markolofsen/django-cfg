'use client';

import { useCallback } from 'react';

import { getDialog } from '@djangocfg/ui-core/lib/dialog-service';

import type {
  TreeAdapter,
  TreeItemId,
  TreeLabels,
  TreeNode,
} from '../../types';
import type { Action } from '../state';

export interface UseRenameOptions<T> {
  dispatch: React.Dispatch<Action>;
  adapter?: TreeAdapter<T>;
  /** Master switch — hooks honour it on every entrypoint. */
  enableInlineRename: boolean;
  nodeById: Map<TreeItemId, TreeNode<T>>;
  getItemName: (node: TreeNode<T>) => string;
  labels: TreeLabels;
}

export interface UseRenameReturn {
  /** True only when both the host opted in AND adapter exposes `rename`. */
  enabled: boolean;
  startRename: (id: TreeItemId) => void;
  cancelRename: () => void;
  commitRename: (id: TreeItemId, nextName: string) => Promise<boolean>;
}

/**
 * Inline rename callbacks. The visible UI lives in `TreeRenameInput`;
 * this hook owns the start/cancel/commit transitions and dialog-driven
 * error surfacing.
 */
export function useRename<T>({
  dispatch,
  adapter,
  enableInlineRename,
  nodeById,
  getItemName,
  labels,
}: UseRenameOptions<T>): UseRenameReturn {
  const enabled = enableInlineRename && !!adapter?.rename;

  const startRename = useCallback(
    (id: TreeItemId) => {
      if (!enableInlineRename) return;
      if (!adapter?.rename) {
        if (process.env.NODE_ENV !== 'production') {
          console.warn(
            '[Tree] startRename called but adapter.rename is not defined.',
          );
        }
        return;
      }
      dispatch({ type: 'start-rename', id });
    },
    [dispatch, enableInlineRename, adapter],
  );

  const cancelRename = useCallback(
    () => dispatch({ type: 'stop-rename' }),
    [dispatch],
  );

  const commitRename = useCallback(
    async (id: TreeItemId, nextName: string): Promise<boolean> => {
      if (!adapter?.rename) {
        dispatch({ type: 'stop-rename' });
        return false;
      }
      const node = nodeById.get(id);
      if (!node) {
        dispatch({ type: 'stop-rename' });
        return false;
      }
      const trimmed = nextName.trim();
      if (trimmed === getItemName(node)) {
        dispatch({ type: 'stop-rename' });
        return true;
      }
      let err: string | null = null;
      if (trimmed === '') err = labels.invalidNameEmpty;
      else err = adapter.validateName?.(trimmed, { node }) ?? null;

      if (err) {
        const dialog = getDialog();
        await dialog?.alert({ title: labels.error, message: err });
        return false;
      }

      try {
        await adapter.rename(node, trimmed);
      } catch (e) {
        const dialog = getDialog();
        await dialog?.alert({
          title: labels.error,
          message: e instanceof Error ? e.message : String(e),
        });
        return false;
      }
      dispatch({ type: 'stop-rename' });
      return true;
    },
    [dispatch, adapter, nodeById, getItemName, labels],
  );

  return { enabled, startRename, cancelRename, commitRename };
}

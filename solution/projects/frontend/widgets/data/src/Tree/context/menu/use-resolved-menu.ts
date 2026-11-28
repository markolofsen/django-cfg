'use client';

import { useMemo } from 'react';

import type { ClipboardState } from '../../data/clipboard';
import type {
  TreeAdapter,
  TreeBuiltinAction,
  TreeContextMenuActionsResolver,
  TreeContextMenuItem,
  TreeItemId,
  TreeLabels,
  TreeMovePosition,
  TreeNode,
  TreeRowRenderProps,
} from '../../types';

export type { TreeContextMenuActionsResolver };
import {
  buildDefaultMenuItems,
  type BuiltinActionContext,
} from './builtin-actions';

/**
 * Internal row-driven resolver — same shape as
 * `TreeContextMenuActionsResolver` but takes a plain `TreeRowRenderProps`
 * instead of the context-with-selection. The provider injects
 * `selectedNodes` itself.
 */
export type ResolvedMenuResolver<T> = (
  row: TreeRowRenderProps<T>,
) => TreeContextMenuItem<T>[] | null | undefined;

export interface UseResolvedMenuOptions<T> {
  adapter?: TreeAdapter<T>;
  contextMenuActions?: TreeContextMenuActionsResolver<T>;
  defaultMenuItems?: TreeBuiltinAction[];
  labels: TreeLabels;
  selected: ReadonlySet<TreeItemId>;
  clipboard: ClipboardState;
  nodeById: Map<TreeItemId, TreeNode<T>>;
  getItemName: (node: TreeNode<T>) => string;
  enableInlineRename: boolean;
  startRename: (id: TreeItemId) => void;
  cutToClipboard: (ids: TreeItemId[]) => void;
  copyToClipboard: (ids: TreeItemId[]) => void;
  pasteFromClipboard: (
    target: TreeNode<T> | null,
    position?: TreeMovePosition,
  ) => Promise<void>;
}

/**
 * Build the merged declarative menu resolver — built-in adapter actions
 * (filtered by `defaultMenuItems`) prepended to the consumer's
 * `contextMenuActions` result. Returns `undefined` when neither side
 * supplies anything, so `TreeRow` can skip rendering a menu entirely.
 *
 * The resolver injects `selectedNodes` on every call so the consumer's
 * resolver receives the multi-selection without having to read it from
 * elsewhere. Finder/Explorer convention applies: if the right-clicked
 * row isn't in the current selection, the menu acts on a single-row
 * effective selection (the row itself).
 */
export function useResolvedMenu<T>(
  opts: UseResolvedMenuOptions<T>,
): ResolvedMenuResolver<T> | undefined {
  const {
    adapter,
    contextMenuActions,
    defaultMenuItems,
    labels,
    selected,
    clipboard,
    nodeById,
    getItemName,
    enableInlineRename,
    startRename,
    cutToClipboard,
    copyToClipboard,
    pasteFromClipboard,
  } = opts;

  return useMemo<ResolvedMenuResolver<T> | undefined>(() => {
    if (!adapter && !contextMenuActions) return undefined;

    return (rowProps) => {
      const selectedIds = selected.has(rowProps.node.id)
        ? [...selected]
        : [rowProps.node.id];
      const selectedNodes = selectedIds
        .map((id) => nodeById.get(id))
        .filter((n): n is TreeNode<T> => !!n);

      const builtin = adapter
        ? buildDefaultMenuItems<T>(
            {
              adapter,
              labels,
              selectedNodes,
              targetNode: rowProps.node,
              getName: getItemName,
              startInlineRename:
                enableInlineRename && adapter.rename ? startRename : undefined,
              clipboard: {
                hasItems: !!clipboard && clipboard.ids.length > 0,
                cut: cutToClipboard,
                copy: copyToClipboard,
                paste: () => pasteFromClipboard(rowProps.node, 'inside'),
              },
            } satisfies BuiltinActionContext<T>,
            defaultMenuItems
              ? (defaultMenuItems as (TreeBuiltinAction | 'separator')[])
              : undefined,
          )
        : null;

      const user =
        contextMenuActions?.({ ...rowProps, selectedNodes }) ?? null;

      if (!builtin && !user) return null;
      if (!user) return builtin;
      if (!builtin) return user;
      return [...builtin, 'separator', ...user];
    };
  }, [
    adapter,
    contextMenuActions,
    defaultMenuItems,
    labels,
    selected,
    clipboard,
    nodeById,
    getItemName,
    enableInlineRename,
    startRename,
    cutToClipboard,
    copyToClipboard,
    pasteFromClipboard,
  ]);
}

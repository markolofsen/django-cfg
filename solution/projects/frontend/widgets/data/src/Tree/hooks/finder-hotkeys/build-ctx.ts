'use client';

import type { BuiltinActionContext } from '../../context/menu';
import type {
  TreeAdapter,
  TreeItemId,
  TreeLabels,
  TreeNode,
} from '../../types';

export interface BuildCtxInput<T> {
  adapter?: TreeAdapter<T>;
  labels: TreeLabels;
  selected: ReadonlySet<TreeItemId>;
  focused: TreeItemId | null;
  getNodeById: (id: TreeItemId) => TreeNode<T> | undefined;
  getItemName: (node: TreeNode<T>) => string;
  startInlineRename?: (id: TreeItemId) => void;
  clipboard?: BuiltinActionContext<T>['clipboard'];
}

/**
 * Build a `BuiltinActionContext<T>` snapshot from the current Tree state.
 * Returns `null` when the adapter is missing — the hotkey handlers
 * short-circuit on null so no built-in action fires without an adapter.
 */
export function buildBuiltinCtx<T>(
  input: BuildCtxInput<T>,
): BuiltinActionContext<T> | null {
  if (!input.adapter) return null;
  const selectedNodes: TreeNode<T>[] = [];
  for (const id of input.selected) {
    const n = input.getNodeById(id);
    if (n) selectedNodes.push(n);
  }
  const targetNode = input.focused
    ? input.getNodeById(input.focused) ?? null
    : null;
  return {
    adapter: input.adapter,
    labels: input.labels,
    selectedNodes,
    targetNode,
    getName: input.getItemName,
    startInlineRename: input.startInlineRename,
    clipboard: input.clipboard,
  };
}

'use client';

// Public surface — re-exports each types module. External code imports
// from `'../types'` (or `'@djangocfg/widget-data/tree'`) and never touches
// these files directly.

export type { TreeItemId, TreeNode, FlatRow } from './node';
export type { TreeSelectionMode } from './selection';
export type { TreeActivationMode, TreeActivateOptions } from './activation';
export type { TreeLoadChildren } from './loader';
export type { TreeLabels } from './labels';
export { DEFAULT_TREE_LABELS } from './labels';
export type {
  TreeRowRenderProps,
  TreeRowSlot,
  TreeContextMenuSlot,
  TreeContextMenuAction,
  TreeContextMenuItem,
  TreeContextMenuActionsContext,
  TreeContextMenuActionsResolver,
} from './slots';
export type {
  TreeMovePosition,
  TreeAdapter,
  TreeBuiltinAction,
} from './adapter';
export type { TreeRootProps, TreeActionsHandle } from './root-props';

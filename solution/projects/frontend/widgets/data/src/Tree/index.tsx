'use client';

/**
 * Decomposed shadcn-style tree component.
 *
 * Two usage patterns:
 *
 *   1) High-level (most cases):
 *      <TreeRoot data={...} getItemName={...} onSelectionChange={...} />
 *
 *   2) Composition (full control):
 *      <TreeProvider data={...} getItemName={...}>
 *        <TreeSearchInput />
 *        <TreeContent />
 *      </TreeProvider>
 */

export { TreeRoot, TreeRoot as Tree, default as default } from './TreeRoot';
export { FinderTree } from './FinderTree';

export {
  TreeProvider,
  useTreeContext,
  useTreeLabels,
  useTreeRows,
  useTreeSelection,
  useTreeExpansion,
  useTreeFocus,
  useTreeSearch,
  useTreeRename,
  useTreeClipboard,
  useTreeDnd,
  useTreeActions,
} from './context';
export type { TreeProviderProps, TreeContextValue } from './context';

export { useTreeTypeAhead, useTreeKeyboard, useTreeFinderHotkeys } from './hooks';
export type {
  UseTreeTypeAheadOptions,
  UseTreeKeyboardOptions,
  UseTreeFinderHotkeysOptions,
} from './hooks';

export {
  TreeContent,
  TreeRow,
  TreeChevron,
  TreeIcon,
  TreeLabel,
  TreeSearchInput,
  TreeEmpty,
  TreeSkeleton,
  TreeError,
  TreeIndentGuides,
  TreeRenameInput,
  TreeDropIndicator,
  TreeEmptyArea,
} from './components';
export type {
  TreeContentProps,
  TreeRowProps,
  TreeChevronProps,
  TreeIconProps,
  TreeLabelProps,
  TreeSearchInputProps,
  TreeEmptyProps,
  TreeSkeletonProps,
  TreeErrorProps,
  TreeIndentGuidesProps,
  TreeRenameInputProps,
  TreeDropIndicatorProps,
  TreeEmptyAreaProps,
} from './components';

export {
  createChildCache,
  resolveChildren,
  flattenTree,
  loadTreeState,
  saveTreeState,
  clearTreeState,
  createDemoTree,
  DEFAULT_TREE_APPEARANCE,
  resolveAppearance,
  appearanceToStyle,
  splitFileName,
  autoSelectRange,
  resolveDropZone,
  defaultCanDrop,
  TREE_DND_MIME,
} from './data';
export type {
  ChildCache,
  ChildEntry,
  ChildEntryStatus,
  FlattenInput,
  PersistedTreeState,
  DemoNode,
  TreeAppearance,
  ResolvedAppearance,
  TreeDensity,
  TreeAccentIntensity,
  TreeRadius,
  TreeVariant,
  TreeRowSizing,
} from './data';

export { DEFAULT_TREE_LABELS } from './types';
export type {
  TreeActionsHandle,
  TreeRootProps,
  TreeNode,
  TreeItemId,
  TreeLabels,
  TreeSelectionMode,
  TreeActivationMode,
  TreeActivateOptions,
  TreeRowRenderProps,
  TreeRowSlot,
  TreeContextMenuSlot,
  TreeContextMenuAction,
  TreeContextMenuItem,
  TreeContextMenuActionsContext,
  TreeContextMenuActionsResolver,
  TreeLoadChildren,
  TreeAdapter,
  TreeBuiltinAction,
  TreeMovePosition,
  FlatRow,
} from './types';

// The dynamic-import wrapper. Exported here because the subpath resolves to
// this barrel: in the retired ui-tools `lazy.tsx` was reachable from no declared export,
// so `LazyTree` was dead code for every tool but `JsonTree`.
export { LazyTree } from './lazy';

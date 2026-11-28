'use client';

export { createChildCache, getEntry, resolveChildren } from './childCache';
export type { ChildCache, ChildEntry, ChildEntryStatus } from './childCache';
export { flattenTree } from './flatten';
export type { FlattenInput } from './flatten';
export { loadTreeState, saveTreeState, clearTreeState } from './persist';
export type { PersistedTreeState } from './persist';
export { createDemoTree } from './createDemoTree';
export type { DemoNode } from './createDemoTree';
export {
  computeRange,
  selectionFromClick,
  selectionFromMove,
  selectionSelectAll,
  selectionClear,
} from './selection';
export type { SelectionState, ClickModifiers } from './selection';
export { splitFileName, autoSelectRange } from './renameUtils';
export type { SplitName } from './renameUtils';
export { isCutId } from './clipboard';
export type { ClipboardKind, ClipboardEntry, ClipboardState } from './clipboard';
export {
  resolveDropZone,
  defaultCanDrop,
  TREE_DND_MIME,
  TREE_ROOT_DROP_ID,
} from './dnd';
export type { DropZoneInput, CanDropInput } from './dnd';
export {
  DEFAULT_TREE_APPEARANCE,
  resolveAppearance,
  appearanceToStyle,
  radiusClass,
  rowStateClasses,
} from './appearance';
export type {
  TreeAppearance,
  ResolvedAppearance,
  TreeDensity,
  TreeAccentIntensity,
  TreeRadius,
  TreeVariant,
  TreeRowSizing,
} from './appearance';

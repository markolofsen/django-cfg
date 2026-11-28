'use client';

export {
  KanbanProvider,
  useKanbanContext,
} from './context/KanbanContext';
export type {
  KanbanContextValue,
  KanbanProviderProps,
} from './context/KanbanContext';

export {
  Kanban,
  KanbanColumn,
  KanbanCard,
  KanbanDragOverlay,
} from './parts';

export type {
  KanbanProps,
  KanbanCard as KanbanCardType,
  KanbanColumn as KanbanColumnType,
  KanbanDragState,
  KanbanCardId,
  KanbanColumnId,
} from './types';

// The dynamic-import wrapper. Exported here because the subpath resolves to
// this barrel: in the retired ui-tools `lazy.tsx` was reachable from no declared export,
// so `LazyKanban` was dead code for every tool but `JsonTree`.
export { LazyKanban } from './lazy';

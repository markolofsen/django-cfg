'use client';

import { createLazyComponent, LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type { KanbanProps } from './types';

export const LazyKanban = createLazyComponent<KanbanProps>(
  () => import('./parts/Kanban').then((m) => ({ default: m.Kanban })),
  {
    displayName: 'LazyKanban',
    fallback: <LoadingFallback minHeight={400} text="Loading kanban board…" />,
  },
);

// Re-export light surface synchronously
export * from './types';
export {
  KanbanProvider,
  useKanbanContext,
} from './context/KanbanContext';
export type {
  KanbanContextValue,
  KanbanProviderProps,
} from './context/KanbanContext';

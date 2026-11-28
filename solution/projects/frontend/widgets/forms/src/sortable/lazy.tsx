'use client';

/**
 * Lazy-loaded Sortable Component
 */

import { createLazyComponent, LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type {
  SortableProps,
  SortableItemProps,
  SortableHandleProps,
} from './types';

export type {
  SortableProps,
  SortableItemProps,
  SortableHandleProps,
} from './types';

export const LazySortable = createLazyComponent<SortableProps>(
  () => import('./parts/Sortable').then((m) => ({ default: m.Sortable })),
  {
    displayName: 'LazySortable',
    fallback: <LoadingFallback minHeight={100} showText={false} />,
  }
);

export const LazySortableItem = createLazyComponent<SortableItemProps>(
  () => import('./parts/Sortable').then((m) => ({ default: m.SortableItem })),
  {
    displayName: 'LazySortableItem',
    fallback: null,
  }
);

export const LazySortableHandle = createLazyComponent<SortableHandleProps>(
  () => import('./parts/Sortable').then((m) => ({ default: m.SortableHandle })),
  {
    displayName: 'LazySortableHandle',
    fallback: null,
  }
);

'use client';

/**
 * Lazy-loaded SelectionToolbar Component
 */

import { createLazyComponent, LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type {
  SelectionToolbarProps,
  SelectionToolbarContentProps,
  SelectionToolbarActionProps,
} from './types';

export type {
  SelectionToolbarProps,
  SelectionToolbarContentProps,
  SelectionToolbarActionProps,
} from './types';

export const LazySelectionToolbar = createLazyComponent<SelectionToolbarProps>(
  () => import('./parts/SelectionToolbar').then((m) => ({ default: m.SelectionToolbar })),
  {
    displayName: 'LazySelectionToolbar',
    fallback: <LoadingFallback minHeight={100} showText={false} />,
  }
);

export const LazySelectionToolbarContent = createLazyComponent<SelectionToolbarContentProps>(
  () => import('./parts/SelectionToolbar').then((m) => ({ default: m.SelectionToolbarContent })),
  {
    displayName: 'LazySelectionToolbarContent',
    fallback: null,
  }
);

export const LazySelectionToolbarAction = createLazyComponent<SelectionToolbarActionProps>(
  () => import('./parts/SelectionToolbar').then((m) => ({ default: m.SelectionToolbarAction })),
  {
    displayName: 'LazySelectionToolbarAction',
    fallback: null,
  }
);

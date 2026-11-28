'use client';

/**
 * Lazy-loaded Scroller Component
 */

import { createLazyComponent, LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type {
  ScrollerProps,
  ScrollerItemProps,
} from './types';

export type {
  ScrollerProps,
  ScrollerItemProps,
} from './types';

export const LazyScroller = createLazyComponent<ScrollerProps>(
  () => import('./parts/Scroller').then((m) => ({ default: m.Scroller })),
  {
    displayName: 'LazyScroller',
    fallback: <LoadingFallback minHeight={100} showText={false} />,
  }
);

export const LazyScrollerItem = createLazyComponent<ScrollerItemProps>(
  () => import('./parts/Scroller').then((m) => ({ default: m.ScrollerItem })),
  {
    displayName: 'LazyScrollerItem',
    fallback: null,
  }
);

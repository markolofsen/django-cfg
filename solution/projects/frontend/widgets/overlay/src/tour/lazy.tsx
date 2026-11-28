'use client';

/**
 * Lazy-loaded Tour Component
 */

import { createLazyComponent, LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type {
  TourProps,
  TourPopoverProps,
  TourNavigationProps,
} from './types';

export type {
  TourProps,
  TourPopoverProps,
  TourNavigationProps,
} from './types';

export const LazyTour = createLazyComponent<TourProps>(
  () => import('./parts/Tour').then((m) => ({ default: m.Tour })),
  {
    displayName: 'LazyTour',
    fallback: <LoadingFallback minHeight={100} showText={false} />,
  }
);

export const LazyTourPopover = createLazyComponent<TourPopoverProps>(
  () => import('./parts/Tour').then((m) => ({ default: m.TourPopover })),
  {
    displayName: 'LazyTourPopover',
    fallback: null,
  }
);

export const LazyTourNavigation = createLazyComponent<TourNavigationProps>(
  () => import('./parts/Tour').then((m) => ({ default: m.TourNavigation })),
  {
    displayName: 'LazyTourNavigation',
    fallback: null,
  }
);

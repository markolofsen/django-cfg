'use client';

/**
 * Lazy-loaded ScrollSpy Component
 */

import { createLazyComponent, LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type {
  ScrollSpyProps,
  ScrollSpyNavProps,
  ScrollSpyNavItemProps,
  ScrollSpySectionProps,
} from './types';

export type {
  ScrollSpyProps,
  ScrollSpyNavProps,
  ScrollSpyNavItemProps,
  ScrollSpySectionProps,
} from './types';

export const LazyScrollSpy = createLazyComponent<ScrollSpyProps>(
  () => import('./parts/ScrollSpy').then((m) => ({ default: m.ScrollSpy })),
  {
    displayName: 'LazyScrollSpy',
    fallback: <LoadingFallback minHeight={100} showText={false} />,
  }
);

export const LazyScrollSpyNav = createLazyComponent<ScrollSpyNavProps>(
  () => import('./parts/ScrollSpy').then((m) => ({ default: m.ScrollSpyNav })),
  {
    displayName: 'LazyScrollSpyNav',
    fallback: null,
  }
);

export const LazyScrollSpyNavItem = createLazyComponent<ScrollSpyNavItemProps>(
  () => import('./parts/ScrollSpy').then((m) => ({ default: m.ScrollSpyNavItem })),
  {
    displayName: 'LazyScrollSpyNavItem',
    fallback: null,
  }
);

export const LazyScrollSpySection = createLazyComponent<ScrollSpySectionProps>(
  () => import('./parts/ScrollSpy').then((m) => ({ default: m.ScrollSpySection })),
  {
    displayName: 'LazyScrollSpySection',
    fallback: null,
  }
);

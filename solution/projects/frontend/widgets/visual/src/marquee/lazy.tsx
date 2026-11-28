'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { MarqueeProps } from './types';

export const LazyMarquee = createLazyComponent<MarqueeProps>(
  () => import('./Marquee').then((mod) => ({ default: mod.Marquee })),
  {
    displayName: 'LazyMarquee',
    fallback: <div data-slot="marquee-skeleton" className="h-8 w-full animate-pulse rounded-sm bg-muted" />,
  }
);

export type { MarqueeProps } from './types';

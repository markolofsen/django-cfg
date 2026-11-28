'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { FpsProps } from './types';

export const LazyFps = createLazyComponent<FpsProps>(
  () => import('./Fps').then((mod) => ({ default: mod.Fps })),
  {
    displayName: 'LazyFps',
    fallback: <div data-slot="fps-skeleton" className="h-8 w-20 animate-pulse rounded-sm bg-muted" />,
  }
);

export type { FpsProps } from './types';

// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { StatusIndicatorProps } from './types';

export const LazyStatusIndicator = createLazyComponent<StatusIndicatorProps>(
  () => import('./StatusIndicator').then((mod) => ({ default: mod.StatusIndicator })),
  {
    displayName: 'LazyStatusIndicator',
    fallback: (
      <span
        data-slot="status-indicator-skeleton"
        className="inline-flex h-7 w-24 animate-pulse rounded-full bg-muted"
      />
    ),
  },
);

export type { StatusIndicatorProps } from './types';

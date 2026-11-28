// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { ActivityGraphProps } from './types';

export const LazyActivityGraph = createLazyComponent<ActivityGraphProps>(
  () => import('./ActivityGraph').then((mod) => ({ default: mod.ActivityGraph })),
  {
    displayName: 'LazyActivityGraph',
    fallback: (
      <div
        data-slot="activity-graph-skeleton"
        className="h-[120px] w-full animate-pulse rounded-md bg-muted"
      />
    ),
  },
);

export type { ActivityGraphProps, ActivityEntry } from './types';

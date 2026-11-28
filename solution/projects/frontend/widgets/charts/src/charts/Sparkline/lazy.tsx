// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { SparklineProps } from './types';

export const LazySparkline = createLazyComponent<SparklineProps>(
  () => import('./Sparkline').then((mod) => ({ default: mod.Sparkline })),
  {
    displayName: 'LazySparkline',
    fallback: (
      <span
        data-slot="sparkline-skeleton"
        className="inline-block h-8 w-[120px] animate-pulse rounded bg-muted"
      />
    ),
  },
);

export type {
  SparklineProps,
  SparklineColor,
  SparklineVariant,
  SparklineDatum,
} from './types';

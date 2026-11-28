'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { SmoothLineProps } from './types';

export const LazySmoothLine = createLazyComponent<SmoothLineProps>(
  () => import('./SmoothLine').then((mod) => ({ default: mod.SmoothLine })),
  {
    displayName: 'LazySmoothLine',
    fallback: (
      <span
        data-slot="smooth-line-skeleton"
        className="block h-10 w-full animate-pulse rounded bg-muted"
      />
    ),
  },
);

export type {
  SmoothLineProps,
  SmoothLineColor,
  SmoothSeriesOptions,
} from './types';

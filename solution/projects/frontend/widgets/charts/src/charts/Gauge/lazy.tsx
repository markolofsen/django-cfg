'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { GaugeProps } from './types';

export const LazyGauge = createLazyComponent<GaugeProps>(
  () => import('./Gauge').then((mod) => ({ default: mod.GaugeCombined })),
  {
    displayName: 'LazyGauge',
    fallback: <div data-slot="gauge-skeleton" className="h-[120px] w-[120px] animate-pulse rounded-full bg-muted" />,
  }
);

export type { GaugeProps } from './types';

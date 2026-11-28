// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { EnvTableProps } from './types';

export const LazyEnvTable = createLazyComponent<EnvTableProps>(
  () => import('./EnvTable').then((mod) => ({ default: mod.EnvTable })),
  {
    displayName: 'LazyEnvTable',
    fallback: (
      <div
        data-slot="env-table-skeleton"
        className="h-40 w-full animate-pulse rounded-xl bg-muted"
      />
    ),
  },
);

export type { EnvTableProps } from './types';

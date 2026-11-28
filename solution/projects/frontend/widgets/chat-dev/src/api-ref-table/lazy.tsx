// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { ApiRefTableProps } from './types';

export const LazyApiRefTable = createLazyComponent<ApiRefTableProps>(
  () => import('./ApiRefTable').then((mod) => ({ default: mod.ApiRefTable })),
  {
    displayName: 'LazyApiRefTable',
    fallback: (
      <div
        data-slot="api-ref-table-skeleton"
        className="h-48 w-full animate-pulse rounded-xl border border-border bg-muted"
      />
    ),
  },
);

export type { ApiRefTableProps, ApiProp, TypeTag } from './types';

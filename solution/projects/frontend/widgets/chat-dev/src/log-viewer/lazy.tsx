// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { LogViewerProps } from './types';

export const LazyLogViewer = createLazyComponent<LogViewerProps>(
  () => import('./LogViewer').then((mod) => ({ default: mod.LogViewer })),
  {
    displayName: 'LazyLogViewer',
    fallback: (
      <div
        data-slot="log-viewer-skeleton"
        className="flex h-[400px] w-full animate-pulse flex-col gap-2 rounded-xl border border-border/60 bg-card p-3"
      >
        <div className="h-7 w-1/3 rounded bg-muted" />
        <div className="h-5 w-2/3 rounded bg-muted" />
        <div className="flex-1 rounded bg-muted/60" />
      </div>
    ),
  },
);

export type { LogViewerProps } from './types';

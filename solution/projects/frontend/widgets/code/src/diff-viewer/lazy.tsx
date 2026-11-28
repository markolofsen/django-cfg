// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { DiffViewerProps } from './types';

export const LazyDiffViewer = createLazyComponent<DiffViewerProps>(
  () =>
    import('./DiffViewer').then((mod) => ({ default: mod.DiffViewer })),
  {
    displayName: 'LazyDiffViewer',
    fallback: (
      <div
        data-slot="diff-viewer-skeleton"
        className="h-48 w-full animate-pulse rounded-xl border border-border/60 bg-muted"
      />
    ),
  },
);

// `DiffLayout` rides the public subpath too: a consumer that sets the
// viewer's `layout` needs to name the type, and reaching into
// `DiffViewer/types` directly would make a private path public by habit.
export type { DiffViewerProps, DiffLayout } from './types';

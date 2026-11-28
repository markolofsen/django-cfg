// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { RequestViewerProps } from './types';

export const LazyRequestViewer = createLazyComponent<RequestViewerProps>(
  () =>
    import('./RequestViewer').then((mod) => ({
      default: mod.RequestViewer,
    })),
  {
    displayName: 'LazyRequestViewer',
    fallback: (
      <div
        data-slot="request-viewer-skeleton"
        className="h-64 w-full animate-pulse rounded-xl bg-muted"
      />
    ),
  },
);

export type {
  RequestViewerProps,
  RequestViewerTab,
  NetworkRequest,
  HeaderEntry,
  TimingEntry,
} from './types';

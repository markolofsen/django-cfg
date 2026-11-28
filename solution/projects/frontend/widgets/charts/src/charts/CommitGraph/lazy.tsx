// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { CommitGraphProps } from './types';

export const LazyCommitGraph = createLazyComponent<CommitGraphProps>(
  () => import('./CommitGraph').then((mod) => ({ default: mod.CommitGraph })),
  {
    displayName: 'LazyCommitGraph',
    fallback: (
      <div
        data-slot="commit-graph-skeleton"
        className="h-40 w-full animate-pulse rounded-xl bg-muted"
      />
    ),
  },
);

export type {
  CommitGraphProps,
  Commit,
  CommitAuthor,
} from './types';

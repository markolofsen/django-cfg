'use client';

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { RatingProps } from './types';

export const LazyRating = createLazyComponent<RatingProps>(
  () => import('./Rating').then((mod) => ({ default: mod.Rating })),
  {
    displayName: 'LazyRating',
    fallback: (
      <div className="flex gap-1">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="size-5 animate-pulse rounded-sm bg-muted" />
        ))}
      </div>
    ),
  }
);

export type { RatingProps } from './types';

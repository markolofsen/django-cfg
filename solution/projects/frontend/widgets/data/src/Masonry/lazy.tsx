'use client';

import { createLazyComponent, LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type { MasonryProps } from './types';

export const LazyMasonry = createLazyComponent<MasonryProps>(
  () => import('./context/MasonryProvider').then((m) => ({ default: m.Masonry })),
  {
    displayName: 'LazyMasonry',
    fallback: <LoadingFallback minHeight={400} text="Loading masonry…" />,
  },
);

// Re-export light surface synchronously
export * from './types';
export {
  Masonry,
  MasonryItem,
  useMasonryContext,
} from './context/MasonryProvider';

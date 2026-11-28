'use client';

import { createLazyComponent, LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type { TreeRootProps } from './types';

export const LazyTree = createLazyComponent<TreeRootProps<unknown>>(
  () => import('./TreeRoot'),
  {
    displayName: 'LazyTree',
    fallback: <LoadingFallback minHeight={200} text="Loading tree…" />,
  },
);

export type { TreeRootProps };

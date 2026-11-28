'use client';

import { createLazyComponent, LoadingFallback } from '../lazy';
import type { PrettyCodeProps } from './pretty-code';

export type { PrettyCodeProps, PrettyCodeLabels } from './pretty-code';
export type { Language } from 'prism-react-renderer';

/**
 * `PrettyCode` in its own chunk: Prism loads when the first block renders.
 *
 * The placeholder is the shared compact spinner kept inside the code surface,
 * so nothing shifts when the block mounts. Use the eager `./pretty-code` where
 * the block is already on screen with the page (a chat fence), and this where
 * it sits behind a tab or a fold.
 */
export const LazyPrettyCode = createLazyComponent<PrettyCodeProps>(
  () => import('./pretty-code').then((m) => ({ default: m.PrettyCode })),
  {
    displayName: 'LazyPrettyCode',
    fallback: (
      <LoadingFallback minHeight={64} text="Loading code…" className="rounded-sm border border-border bg-muted dark:bg-code" />
    ),
  },
);

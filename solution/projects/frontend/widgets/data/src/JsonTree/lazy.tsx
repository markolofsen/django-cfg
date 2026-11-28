'use client';

/**
 * `@djangocfg/widget-data/json-tree` subpath entrypoint.
 *
 * Single lazy-loaded export (`LazyJsonTree`) wrapping the renderer
 * (~80KB chunk including the toolbar UI). Suspense fallback ships from
 * the shared `LoadingFallback`.
 */

import { createLazyComponent, LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type { JsonTreeProps } from './types';

export type { JsonTreeProps, JsonValue, JsonAction, JsonSize } from './types';

export const LazyJsonTree = createLazyComponent<JsonTreeProps>(
  () => import('./JsonViewer').then((m) => ({ default: m.JsonTree })),
  {
    displayName: 'LazyJsonTree',
    fallback: <LoadingFallback minHeight={64} text="Loading JSON viewer…" />,
  },
);

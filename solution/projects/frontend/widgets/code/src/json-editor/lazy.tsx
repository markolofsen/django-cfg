'use client';

/**
 * `@djangocfg/widget-code/json-editor` subpath entrypoint.
 *
 * Heavy editor (~58 KB minified for `json-edit-react` alone). Lazy-load
 * so consumers that only display JSON pay nothing — they should use
 * `@djangocfg/widget-data/json-tree` instead, which is ~10× lighter.
 */

import { createLazyComponent, LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type { JsonEditorProps } from './JsonEditor';

export type { JsonEditorProps } from './JsonEditor';

export const LazyJsonEditor = createLazyComponent<JsonEditorProps>(
  () => import('./JsonEditor').then((m) => ({ default: m.JsonEditor })),
  {
    displayName: 'LazyJsonEditor',
    fallback: <LoadingFallback minHeight={120} text="Loading JSON editor…" />,
  },
);

export { LazyJsonEditor as JsonEditor };

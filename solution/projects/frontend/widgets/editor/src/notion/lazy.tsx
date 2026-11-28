'use client';

/**
 * `@djangocfg/widget-editor/notion` subpath entrypoint.
 *
 * `NotionEditor` is a TipTap WYSIWYG with the full Notion-style stack:
 * StarterKit + Markdown + Highlight + Table + TaskList + CodeBlockLowlight
 * + GlobalDragHandle + a custom `/` slash menu. The full bundle including
 * lowlight's `common` language pack lands around ~350KB minified — wrap
 * the component in React.lazy so pages that don't render the editor pay
 * nothing.
 *
 * Why a hand-rolled lazy wrapper (mirrors MarkdownEditor/lazy.tsx):
 * `createLazyComponent` returns a plain function component that does not
 * forward `ref`, so the imperative `NotionEditorHandle` would be silently
 * dropped. The wrapper below is a `forwardRef` so the ref reaches the
 * underlying TipTap editor through `React.lazy`.
 */

import { Suspense, forwardRef, lazy } from 'react';
import { LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type { NotionEditorHandle, NotionEditorProps } from './types';

const NotionEditorImpl = lazy(() =>
  import('./NotionEditor').then((m) => ({ default: m.NotionEditor })),
);

export const LazyNotionEditor = forwardRef<NotionEditorHandle, NotionEditorProps>(
  function LazyNotionEditor(props, ref) {
    return (
      <Suspense fallback={<LoadingFallback minHeight={240} text="Loading editor…" />}>
        <NotionEditorImpl {...props} ref={ref} />
      </Suspense>
    );
  },
);

// `NotionEditor` is the public eager-looking name — it resolves to the
// same lazy component so importing it from this subpath does NOT pull
// ~350KB of TipTap + lowlight into the caller's initial bundle.
export { LazyNotionEditor as NotionEditor };

export type { NotionEditorHandle, NotionEditorProps } from './types';
export type { SlashItem } from './slashItems';

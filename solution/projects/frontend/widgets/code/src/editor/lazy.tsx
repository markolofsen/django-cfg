'use client';

/**
 * `@djangocfg/widget-code/editor` subpath entrypoint.
 *
 * Monaco itself weighs ~550 KB minified — we must never pay that cost
 * unless the editor actually mounts. The `Lazy*` wrappers here dynamically
 * import the `Editor` and `DiffEditor` components, which transitively pull
 * in `monaco-editor` and the worker setup.
 *
 * The rest of the surface (types, EditorProvider, useMonaco hook, helpers)
 * is light:
 *   - `monaco-editor` is referenced only as a TS type (`type *`) — erased
 *     at compile time.
 *   - `useMonaco` performs a dynamic `import('monaco-editor')` itself, so
 *     importing the hook is free until the caller actually invokes it.
 *
 * That means consumers can wire up keyboard shortcuts, theme toggles, or
 * file-state hooks at the top of their tree without paying Monaco's cost,
 * and only render `<LazyEditor>` lower in the tree where it's needed.
 */

import { createLazyComponent, LoadingFallback } from '@djangocfg/widget-kit/lazy';
import type { EditorProps, DiffEditorProps } from './types';

// ============================================================================
// Lazy components
// ============================================================================

export const LazyEditor = createLazyComponent<EditorProps>(
  () => import('./components/Editor').then((m) => ({ default: m.Editor })),
  {
    displayName: 'LazyEditor',
    fallback: <LoadingFallback minHeight={320} text="Loading editor…" />,
  },
);

export const LazyDiffEditor = createLazyComponent<DiffEditorProps>(
  () => import('./components/DiffEditor').then((m) => ({ default: m.DiffEditor })),
  {
    displayName: 'LazyDiffEditor',
    fallback: <LoadingFallback minHeight={320} text="Loading diff editor…" />,
  },
);

// `Editor` / `DiffEditor` are the plain named exports — same lazy components,
// kept so callers can `import { Editor } from '@djangocfg/widget-code/editor'`
// without knowing about the `Lazy*` naming.
export { LazyEditor as Editor };
export { LazyDiffEditor as DiffEditor };

// ============================================================================
// Light surface
// ============================================================================

// Hooks — `useMonaco` does its own dynamic import; the others are pure.
export {
  useMonaco,
  useEditor,
  useLanguage,
  useEditorTheme,
} from './hooks';

// Provider + context hook
export { EditorProvider, useEditorContext } from './context';

// All types
export type {
  EditorFile,
  EditorOptions,
  EditorProps,
  EditorContextValue,
  UseEditorReturn,
  UseMonacoReturn,
  DiffEditorProps,
} from './types';

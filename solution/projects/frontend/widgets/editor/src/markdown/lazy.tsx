'use client';

/**
 * `@djangocfg/widget-editor/markdown` subpath entrypoint.
 *
 * `MarkdownEditor` is a TipTap WYSIWYG with the full ProseMirror + TipTap
 * extension stack — `@tiptap/react`, `starter-kit`, `markdown`, `mention`,
 * `placeholder`, plus our `createMentionSuggestion` (floating-ui anchored
 * dropdown). Together that's ~200 KB minified — wrap it in React.lazy so
 * pages that don't render an editor don't pay.
 *
 * Why a hand-rolled lazy wrapper instead of `createLazyComponent`:
 * `createLazyComponent` returns a plain function component that does not
 * forward `ref`, so the imperative `MarkdownEditorHandle` (focus /
 * moveCursorToEnd — used by chat composer registration + voice slot)
 * would be silently dropped. The wrapper below is a `forwardRef` so the
 * ref reaches the underlying TipTap editor through `React.lazy`.
 *
 * Light surface kept here:
 *   - All public types (erased at compile time).
 *   - `mentionPresets` — pure data describing how to render mentions to
 *     markdown. No TipTap imports at module scope.
 */

import { Suspense, lazy, forwardRef } from 'react';
import { InlineLoadingFallback } from '@djangocfg/widget-kit/lazy';
import type { MarkdownEditorProps, MarkdownEditorHandle } from './MarkdownEditor';

const MarkdownEditorImpl = lazy(() =>
  import('./MarkdownEditor').then((m) => ({ default: m.MarkdownEditor })),
);

/**
 * Lazy-loaded `MarkdownEditor`. Forwards `ref` (`MarkdownEditorHandle`)
 * to the underlying TipTap editor once the chunk resolves.
 */
export const LazyMarkdownEditor = forwardRef<MarkdownEditorHandle, MarkdownEditorProps>(
  function LazyMarkdownEditor(props, ref) {
    // Input-sized, not panel-sized: this editor IS the composer's text field,
    // so the 140px tinted block with a 32px disc and a caption was out of
    // scale and shifted the layout when TipTap mounted. A bare 14px spinner is
    // enough — the wait is short and nothing is actionable during it. The
    // label survives for screen readers.
    return (
      <Suspense fallback={<InlineLoadingFallback />}>
        <MarkdownEditorImpl {...props} ref={ref} />
      </Suspense>
    );
  },
);

// `MarkdownEditor` is the public eager-looking name — it resolves to the
// same lazy component so importing it from this subpath does NOT pull
// ~200 KB of TipTap into the caller's initial bundle. Keeping the name
// here means `@djangocfg/widget-editor/markdown` exposes
// `MarkdownEditor`, `LazyMarkdownEditor`, and `mentionPresets`.
export { LazyMarkdownEditor as MarkdownEditor };

// Light surface — pure helpers + types.
export { mentionPresets } from './mentionPresets';

// File-path chip — the standalone presentational chip + the pure detector
// helpers. The chip is light enough to export eagerly (no TipTap at module
// scope — it only pulls `FileIcon` + the pure detector), so consumers can
// render a known path outside the editor without loading the ~200 KB
// TipTap chunk.
export { FilePathChip } from './filePath/FilePathChip';
export type { FilePathChipProps } from './filePath/FilePathChip';
export { findFilePaths, splitPath, truncatePathLabel } from './filePath/detect';
export type { FilePathMatch, SplitPath, TruncateOptions } from './filePath/detect';

export type {
  MarkdownEditorProps,
  MarkdownEditorHandle,
} from './MarkdownEditor';

export type {
  MentionItem,
  MentionConfig,
  MentionAttrs,
  MentionMarkdownRenderer,
} from './types';

// Slash command surface — opt-in by passing `slashCommands` to
// `MarkdownEditor` (or `<ComposerRichTextarea>`, which forwards). The
// node itself is mounted by the editor on first render. `SlashCommandInfo`
// is structurally compatible with the chat package's `SlashCommand`.
export type { SlashCommandInfo } from './slash/types';

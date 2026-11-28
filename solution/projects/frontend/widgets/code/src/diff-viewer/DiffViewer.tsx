// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// Line-by-line code diff viewer. Supports unified (single column) and
// split (side-by-side) layouts. Syntax highlighting reuses the same
// `prism-react-renderer` bundle that the `PrettyCode` tool already
// pulls in — no second highlighter is loaded.
//
// Requires <UiProviders> at the host root (no nested providers here).
// See CONTRACT.md §5.
//
// Unlike `PrettyCode` (intentionally always-dark), DiffViewer adapts to
// the host theme. Diffs are commonly embedded in documentation pages
// where forcing a dark surface on a light page reads as a bug. The
// Prism theme is picked per host theme (`themes.vsDark` for dark,
// `themes.github` for light) and surface chrome uses semantic tokens.

'use client';

import * as React from 'react';
import { themes, type PrismTheme } from 'prism-react-renderer';
import { cn } from '@djangocfg/ui-core/lib';
import { useResolvedTheme } from '@djangocfg/ui-core/hooks';
import { CopyButton } from './components/CopyButton';
import { SplitView } from './components/SplitView';
import { UnifiedView } from './components/UnifiedView';
import { useDiff } from './hooks/useDiff';
import { useDiffLanguage } from './hooks/useHighlighter';
import {
  DIFF_TONE_CLASSES,
  type DiffInput,
  type DiffViewerProps,
} from './types';

export function DiffViewer({
  layout = 'unified',
  language,
  oldTitle,
  newTitle,
  copyable = true,
  context = 3,
  hostScrolls = false,
  className,
  ...allProps
}: DiffViewerProps) {
  // Split the diff-input keys off the DOM rest props so we don't spread
  // `oldCode` / `newCode` / `patch` onto the wrapping <div>.
  const { oldCode, newCode, patch, ...divProps } =
    allProps as DiffViewerProps & Record<string, unknown>;
  const input: DiffInput =
    patch !== undefined
      ? ({ patch: patch as string } as DiffInput)
      : ({
          oldCode: (oldCode as string) ?? '',
          newCode: (newCode as string) ?? '',
        } as DiffInput);

  const { lines, numWidth, stats } = useDiff({ input, context });

  // Longest content line in ch — the shared minimum width of the content
  // column in BOTH layouts. A single global value (like `numWidth`) keeps
  // every row the same width, so the whole block scrolls as one unit inside
  // the outer `overflow-x-auto` wrapper below, and split-view columns stay
  // aligned across rows. Tabs render 8ch wide under `whitespace-pre`, so
  // they count as 8.
  const maxContentCh = React.useMemo(() => {
    let max = 0;
    for (const l of lines) {
      const tabs = (l.content.match(/\t/g) ?? []).length;
      // CJK / fullwidth glyphs are one UTF-16 unit but render two columns
      // wide in monospace — count them twice. (Emoji are already two units.)
      const wide = (l.content.match(/[\u2E80-\u9FFF\uF900-\uFAFF\uFF01-\uFF60]/g) ?? []).length;
      const len = l.content.length + tabs * 7 + wide;
      if (len > max) max = len;
    }
    return max;
  }, [lines]);

  // Pass `null` when no language → cheap plain-text render path.
  const prismLang = useDiffLanguage(language);
  const resolvedLanguage = language ? prismLang : null;

  // Pick a Prism palette to match the host theme. Resolved once at the
  // viewer root, then forwarded to every line — keeps the hook out of
  // per-line render paths (could be thousands of rows on big diffs).
  const resolved = useResolvedTheme();
  const prismTheme: PrismTheme =
    resolved === 'dark' ? themes.vsDark : themes.github;

  // Full text used for the copy button — concatenates current lines as
  // displayed, including removed ones. Mirrors jalcoui's behavior.
  const fullCode = React.useMemo(
    () => lines.map((l) => l.content).join('\n'),
    [lines],
  );

  const showHeader = Boolean(oldTitle || newTitle);
  const addedTone = DIFF_TONE_CLASSES.added.stat;
  const removedTone = DIFF_TONE_CLASSES.removed.stat;

  return (
    <div
      data-slot="diff-viewer"
      data-layout={layout}
      className={cn(
        'relative overflow-hidden rounded-xl border border-border/60 bg-card text-foreground shadow-sm',
        className,
      )}
      {...(divProps as React.ComponentProps<'div'>)}
    >
      {showHeader && (
        <div className="flex items-center justify-between gap-3 border-b border-border/60 bg-muted/40 px-4 py-2.5">
          <div className="flex items-center gap-3 text-sm">
            {oldTitle && (
              <span className="text-muted-foreground">{oldTitle}</span>
            )}
            {oldTitle && newTitle && (
              <span className="text-muted-foreground/60" aria-hidden="true">
                →
              </span>
            )}
            {newTitle && (
              <span className="font-medium text-foreground">{newTitle}</span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs tabular-nums">
              {stats.added > 0 && (
                <span className={addedTone}>+{stats.added}</span>
              )}
              {stats.removed > 0 && (
                <span className={removedTone}>-{stats.removed}</span>
              )}
            </div>
            {copyable && <CopyButton value={fullCode} />}
          </div>
        </div>
      )}

      {!showHeader && copyable && (
        <div className="absolute right-2 top-2 z-10">
          <CopyButton value={fullCode} />
        </div>
      )}

      <div className="overflow-x-auto">
        {layout === 'split' ? (
          <SplitView
            lines={lines}
            numWidth={numWidth}
            maxContentCh={maxContentCh}
            language={resolvedLanguage}
            prismTheme={prismTheme}
            hostScrolls={hostScrolls}
          />
        ) : (
          <UnifiedView
            lines={lines}
            numWidth={numWidth}
            maxContentCh={maxContentCh}
            language={resolvedLanguage}
            prismTheme={prismTheme}
            hostScrolls={hostScrolls}
          />
        )}
      </div>
    </div>
  );
}

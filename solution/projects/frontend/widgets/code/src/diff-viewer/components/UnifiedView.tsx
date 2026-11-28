// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import * as React from 'react';
import type { Language, PrismTheme } from 'prism-react-renderer';
import { Virtuoso } from 'react-virtuoso';
import { cn } from '@djangocfg/ui-core/lib';
import { DIFF_TONE_CLASSES, type DiffLine } from '../types';
import { DiffLineContent } from './DiffLineContent';

interface UnifiedViewProps {
  lines: DiffLine[];
  numWidth: number;
  /** Longest content line in ch (global, from the viewer root) — shared
   * minimum width of the content column, so every row is equally wide and the
   * outer `overflow-x-auto` scrolls the block with full-bleed row tints. */
  maxContentCh: number;
  language: Language | null;
  prismTheme: PrismTheme;
  /** The host already caps this block's height and owns the scroller, so the
   *  virtualized path must not open a second one inside it. */
  hostScrolls?: boolean;
}

function linePrefix(type: DiffLine['type']) {
  if (type === 'added') return '+';
  if (type === 'removed') return '-';
  return ' ';
}

// Threshold above which we switch from a plain DOM table to a virtualized
// list. Mirrors LogViewer — under this size the DOM stays debuggable;
// above it tokenization + layout of thousands of rows starts to dominate
// scroll.
const VIRTUALIZE_THRESHOLD = 100;
// Height of the scrolling viewport when virtualized. Kept here (not a prop)
// because every existing consumer expects the viewer to expand to its
// content; only the >100-line path needs a fixed window to virtualize.
//
// A HOST THAT ALREADY CAPS THE HEIGHT MUST SAY SO (`hostScrolls`). Chat used
// to wrap this in its own 480px `overflowY:auto` box while Virtuoso opened a
// second 480px scroller inside it — two scrollers of identical height, neither
// owning the scroll position Virtuoso measures against. Virtuoso then sized its
// spacers against a viewport it did not control and left ~250px of blank list
// between two consecutively-numbered rows, which reads as "the diff lost some
// lines" when nothing was lost at all.
const VIRTUAL_VIEWPORT_HEIGHT = 480;

interface RowProps {
  line: DiffLine;
  numWidth: number;
  maxContentCh: number;
  language: Language | null;
  prismTheme: PrismTheme;
}

/**
 * One unified-diff row. CSS grid (not a table cell) so a `<Virtuoso>`
 * list can virtualize identical rows without a host `<table>` (the
 * `display: table-row-group` virtual scrollers force on `<tbody>` doesn't
 * play with arbitrary row heights).
 */
function Row({ line, numWidth, maxContentCh, language, prismTheme }: RowProps) {
  const tone = DIFF_TONE_CLASSES[line.type];
  const gutterCh = `calc(${numWidth}ch + 1rem)`;
  // Same global minimum as SplitView: every row renders at the width of the
  // longest line, so row background tints stay full-bleed while the outer
  // `overflow-x-auto` scrolls the whole block.
  const contentCh = `minmax(calc(${maxContentCh}ch + 1.5rem), 1fr)`;
  return (
    <div
      className={cn(
        'grid items-start font-mono text-[13px] leading-relaxed',
        tone.row,
      )}
      style={{
        gridTemplateColumns: `${gutterCh} ${gutterCh} 1.5rem ${contentCh}`,
      }}
    >
      <div
        className={cn(
          'select-none px-2 text-right tabular-nums whitespace-nowrap',
          tone.num,
        )}
      >
        {line.oldNumber ?? ''}
      </div>
      <div
        className={cn(
          'select-none px-2 text-right tabular-nums whitespace-nowrap',
          tone.num,
        )}
      >
        {line.newNumber ?? ''}
      </div>
      <div
        className={cn(
          'select-none text-center whitespace-nowrap',
          tone.num,
        )}
      >
        {linePrefix(line.type)}
      </div>
      <div className={cn('whitespace-pre px-3', tone.text)}>
        <DiffLineContent
          content={line.content}
          language={language}
          prismTheme={prismTheme}
        />
      </div>
    </div>
  );
}

/**
 * Single-column unified diff. Two gutters on the left carry the old / new
 * line numbers, the third (narrow) column is the +/-/space prefix, then
 * the content. Background tint per row signals the change kind.
 *
 * The gutter widths come from the globally-computed `numWidth` (passed
 * down from the viewer root). Using CSS grid with the same explicit
 * `gridTemplateColumns` on every row guarantees pixel-identical gutters
 * across all rows, even when content sizes vary.
 *
 * Diffs above {@link VIRTUALIZE_THRESHOLD} lines render through
 * `<Virtuoso>` so 1k–10k-line diffs don't lock the main thread.
 */
export function UnifiedView({
  lines,
  numWidth,
  maxContentCh,
  language,
  prismTheme,
  hostScrolls = false,
}: UnifiedViewProps) {
  // A host that caps the height owns the scroller; virtualizing inside it would
  // nest a second one of the same size (see VIRTUAL_VIEWPORT_HEIGHT). Render
  // every row plainly instead.
  //
  // The DOM cost is bounded by the PRODUCER, not by hope: cmdop's agent caps a
  // patch at 400 changed lines (`diffcompute.go: maxChangedLines`) and sends
  // stats-only above that, so a chat diff tops out around a thousand rows
  // including context — an order of magnitude below where virtualization earns
  // its keep. What it buys back is what GitHub publicly lost when it
  // virtualized its own diff view: Ctrl+F, select-all and printing. diff2html
  // and react-diff-view ship without virtualization for the same reason.
  if (lines.length > VIRTUALIZE_THRESHOLD && !hostScrolls) {
    return (
      <div data-slot="diff-viewer-unified">
        <Virtuoso
          data={lines}
          style={{ height: VIRTUAL_VIEWPORT_HEIGHT }}
          // `initialItemCount` forces SSR-style initial render so rows
          // appear immediately on first paint instead of waiting for
          // ResizeObserver — without it, embedded iframes (Storybook,
          // docs sites) sometimes start at zero height and the list
          // stays empty until a window resize.
          initialItemCount={Math.min(lines.length, 30)}
          itemContent={(_, line) => (
            <Row
              line={line}
              numWidth={numWidth}
              maxContentCh={maxContentCh}
              language={language}
              prismTheme={prismTheme}
            />
          )}
          increaseViewportBy={{ top: 200, bottom: 400 }}
        />
      </div>
    );
  }

  return (
    <div data-slot="diff-viewer-unified">
      {lines.map((line, i) => (
        <Row
          key={i}
          line={line}
          numWidth={numWidth}
          maxContentCh={maxContentCh}
          language={language}
          prismTheme={prismTheme}
        />
      ))}
    </div>
  );
}

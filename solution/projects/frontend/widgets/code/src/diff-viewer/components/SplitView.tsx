// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import * as React from 'react';
import type { Language, PrismTheme } from 'prism-react-renderer';
import { Virtuoso } from 'react-virtuoso';
import { cn } from '@djangocfg/ui-core/lib';
import { DIFF_TONE_CLASSES, type DiffLine } from '../types';
import { DiffLineContent } from './DiffLineContent';

interface SplitViewProps {
  lines: DiffLine[];
  numWidth: number;
  /** Longest content line in ch (global, from the viewer root) — the shared
   * minimum width of every content cell, so all rows are equally wide and the
   * OUTER `overflow-x-auto` scrolls the whole block as one unit. Before this,
   * each content cell carried its own `overflow-x-auto` and every line
   * scrolled independently. */
  maxContentCh: number;
  language: Language | null;
  prismTheme: PrismTheme;
  /** The host already caps this block's height and owns the scroller, so the
   *  virtualized path must not open a second one inside it. */
  hostScrolls?: boolean;
}

// See UnifiedView for context — same threshold + viewport size keeps both
// layouts behaviorally aligned.
const VIRTUALIZE_THRESHOLD = 100;
const VIRTUAL_VIEWPORT_HEIGHT = 480;

/**
 * Align consecutive `removed` / `added` runs into a pair of columns.
 * Pure-add rows leave the left column empty; pure-remove rows leave the
 * right column empty. Context rows duplicate on both sides.
 *
 * The pairing is the same shape jalcoui ships — we keep it so downstream
 * consumers' visual baseline doesn't move.
 */
function pairLines(lines: DiffLine[]): Array<{
  left: DiffLine | null;
  right: DiffLine | null;
}> {
  const pairs: Array<{ left: DiffLine | null; right: DiffLine | null }> = [];

  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (line === undefined) {
      i++;
      continue;
    }
    if (line.type === 'context') {
      pairs.push({ left: line, right: line });
      i++;
      continue;
    }
    if (line.type === 'removed') {
      const removed: DiffLine[] = [];
      for (let next = lines[i]; next !== undefined && next.type === 'removed'; next = lines[i]) {
        removed.push(next);
        i++;
      }
      const added: DiffLine[] = [];
      for (let next = lines[i]; next !== undefined && next.type === 'added'; next = lines[i]) {
        added.push(next);
        i++;
      }
      const maxLen = Math.max(removed.length, added.length);
      for (let j = 0; j < maxLen; j++) {
        pairs.push({
          left: removed[j] ?? null,
          right: added[j] ?? null,
        });
      }
      continue;
    }
    // line.type === 'added' with no preceding removed run
    pairs.push({ left: null, right: line });
    i++;
  }

  return pairs;
}

function sidePrefix(side: 'old' | 'new', type: DiffLine['type'] | undefined) {
  if (!type || type === 'context') return ' ';
  if (side === 'old' && type === 'removed') return '-';
  if (side === 'new' && type === 'added') return '+';
  return ' ';
}

interface HalfProps {
  line: DiffLine | null;
  side: 'old' | 'new';
  numWidth: number;
  maxContentCh: number;
  language: Language | null;
  prismTheme: PrismTheme;
}

function Half({ line, side, numWidth, maxContentCh, language, prismTheme }: HalfProps) {
  const tone = line ? DIFF_TONE_CLASSES[line.type] : DIFF_TONE_CLASSES.context;
  const gutterCh = `calc(${numWidth}ch + 1rem)`;
  // The content track's MINIMUM is the longest line in the whole diff (+ the
  // cell's own 1.5rem horizontal padding). Every row therefore renders at the
  // same width: short diffs still stretch to fill (1fr), long diffs push the
  // row past the container so the viewer-level `overflow-x-auto` scrolls the
  // whole block — never one line at a time.
  const contentCh = `minmax(calc(${maxContentCh}ch + 1.5rem), 1fr)`;
  return (
    <div
      className={cn('grid items-start', tone.row)}
      style={{
        gridTemplateColumns: `${gutterCh} 1.5rem ${contentCh}`,
      }}
    >
      <div
        className={cn(
          'select-none px-2 text-right tabular-nums whitespace-nowrap',
          tone.num,
        )}
      >
        {(side === 'old' ? line?.oldNumber : line?.newNumber) ?? ''}
      </div>
      <div
        className={cn(
          'select-none text-center whitespace-nowrap',
          tone.num,
        )}
      >
        {sidePrefix(side, line?.type)}
      </div>
      <div
        className={cn(
          // overflow-x-clip: the width math below reserves the longest line,
          // so this never cuts real content — it only stops estimation-error
          // glyph runs (CJK/emoji render wider than their code-unit count)
          // from bleeding under the neighbouring column.
          'whitespace-pre px-3 overflow-x-clip',
          line ? tone.text : 'text-muted-foreground/40',
        )}
      >
        {line ? (
          <DiffLineContent
            content={line.content}
            language={language}
            prismTheme={prismTheme}
          />
        ) : (
          ' '
        )}
      </div>
    </div>
  );
}

interface PairRowProps {
  pair: { left: DiffLine | null; right: DiffLine | null };
  numWidth: number;
  maxContentCh: number;
  language: Language | null;
  prismTheme: PrismTheme;
}

function PairRow({ pair, numWidth, maxContentCh, language, prismTheme }: PairRowProps) {
  // Tailwind's `grid-cols-2` is repeat(2, minmax(0, 1fr)) — the 0 minimum let
  // each column shrink below its Half's reserved width, so the inner grids
  // silently overflowed into each other while the row itself never exceeded
  // the container (the viewer-level scroller never engaged). The columns must
  // carry the SAME deterministic minimum the Half reserves inside: gutter
  // (numWidth ch + 1rem) + 1.5rem prefix + content (maxContentCh ch + 1.5rem
  // padding). Short diffs still split 50/50 (1fr); long diffs push the row
  // wider than the container and the outer `overflow-x-auto` scrolls the
  // whole block.
  const halfMin = `calc(${numWidth}ch + 1rem + 1.5rem + ${maxContentCh}ch + 1.5rem)`;
  return (
    <div
      className="grid font-mono text-[13px] leading-relaxed"
      style={{ gridTemplateColumns: `repeat(2, minmax(${halfMin}, 1fr))` }}
    >
      <div className="border-r border-border/40">
        <Half
          line={pair.left}
          side="old"
          numWidth={numWidth}
          maxContentCh={maxContentCh}
          language={language}
          prismTheme={prismTheme}
        />
      </div>
      <div>
        <Half
          line={pair.right}
          side="new"
          numWidth={numWidth}
          maxContentCh={maxContentCh}
          language={language}
          prismTheme={prismTheme}
        />
      </div>
    </div>
  );
}

/**
 * Side-by-side diff. Left half = old, right half = new. Each row is a
 * single grid wrapping two `<Half>` halves so a `<Virtuoso>` list can
 * virtualize the whole stack with naturally synchronized scrolling.
 *
 * Both halves receive the SAME globally-computed `numWidth` so the two
 * gutter columns are pixel-identical regardless of which side has the
 * longer line numbers.
 */
export function SplitView({
  lines,
  numWidth,
  maxContentCh,
  language,
  prismTheme,
  hostScrolls = false,
}: SplitViewProps) {
  const pairs = React.useMemo(() => pairLines(lines), [lines]);

  // See UnifiedView: a host that caps the height owns the scroller, and nesting
  // a second one of the same height is what leaves blank bands mid-list.
  if (pairs.length > VIRTUALIZE_THRESHOLD && !hostScrolls) {
    // Virtualized rows share the same global `maxContentCh`, so scroll width
    // stays stable as rows mount/unmount. The Virtuoso scroller owns BOTH
    // axes here (CSS can't mix visible-x with auto-y), which is still
    // whole-block scrolling — just inside the fixed-height viewport.
    return (
      <div data-slot="diff-viewer-split">
        <Virtuoso
          data={pairs}
          style={{ height: VIRTUAL_VIEWPORT_HEIGHT }}
          // See UnifiedView for why `initialItemCount` is required —
          // without it, embedded iframes start with a zero-height list.
          initialItemCount={Math.min(pairs.length, 30)}
          itemContent={(_, pair) => (
            <PairRow
              pair={pair}
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
    <div data-slot="diff-viewer-split">
      {pairs.map((pair, idx) => (
        <PairRow
          key={idx}
          pair={pair}
          numWidth={numWidth}
          maxContentCh={maxContentCh}
          language={language}
          prismTheme={prismTheme}
        />
      ))}
    </div>
  );
}

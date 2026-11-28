// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// Topological git graph with rail lines showing branch forks, merges, and
// commit ancestry. Renders the same visual as GitKraken / Fork / Tower.
//
// Composer only — heavy lifting lives in:
//   - hooks/useGraphLayout.ts    topology pass
//   - hooks/useLaneColors.ts     theme-aware categorical palette
//   - components/Rails.tsx       SVG rails + dot
//   - components/CommitRow.tsx   row body (refs, message, meta)
//   - components/CommitDetail.tsx popover detail
//
// Project rules exercised here: semantic tokens for chrome (no raw scales),
// theme-derived hex colors for SVG strokes (no Tailwind classes inside
// `stroke=`), no nested overlay providers, attribution header, lazy entry.

'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import type { CommitGraphProps } from './types';
import { useGraphLayout } from './hooks/useGraphLayout';
import { useLaneColors, pickLaneColor } from './hooks/useLaneColors';
import { CommitRow } from './components/CommitRow';

function CommitGraph({
  commits,
  truncateHash = 7,
  railWidth = 24,
  className,
  ...props
}: CommitGraphProps) {
  const laneColors = useLaneColors();
  const { rows, maxRails } = useGraphLayout(commits, laneColors);
  const svgWidth = maxRails * railWidth;

  if (rows.length === 0) {
    return (
      <div
        data-slot="commit-graph"
        className={cn(
          'flex items-center justify-center rounded-xl border border-border/60 bg-card py-10 text-sm text-muted-foreground shadow-sm',
          className,
        )}
        {...props}
      >
        No commits.
      </div>
    );
  }

  return (
    <div
      data-slot="commit-graph"
      className={cn(
        'overflow-hidden rounded-xl border border-border/60 bg-card shadow-sm',
        className,
      )}
      style={{ ['--commit-graph-rail-width' as string]: `${svgWidth}px` }}
      {...props}
    >
      <div className="overflow-x-auto">
        {rows.map((row, i) => (
          <CommitRow
            key={`${row.commit.hash}-${i}`}
            row={row}
            prevRow={rows[i - 1] ?? null}
            railWidth={railWidth}
            maxRails={maxRails}
            truncateHash={truncateHash}
            laneColors={laneColors}
            railColor={pickLaneColor(laneColors, row.rail)}
          />
        ))}
      </div>
    </div>
  );
}

export { CommitGraph };

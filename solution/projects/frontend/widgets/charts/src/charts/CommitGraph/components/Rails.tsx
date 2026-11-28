// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import * as React from 'react';
import { useThemeColor } from '@djangocfg/ui-core/styles/palette';
import { ROW_HEIGHT, type GraphRow } from '../types';
import { pickLaneColor } from '../hooks/useLaneColors';

interface RailsProps {
  row: GraphRow;
  prevRow: GraphRow | null;
  railWidth: number;
  maxRails: number;
  laneColors: string[];
}

/**
 * SVG renderer for the rail column of a single commit row.
 *
 * Draws four classes of geometry:
 *   1. Pass-through rails — straight vertical line top→bottom for any rail
 *      that is active above *and* below this row and is not the commit rail.
 *   2. Commit rail incoming/outgoing — half-height verticals on the commit's
 *      own rail, depending on whether the rail was active above/below.
 *   3. Fork-out curves — bezier from the commit's rail down to a freshly
 *      allocated rail (a new branch coming off this commit).
 *   4. Merge curves — bezier from a source rail into the commit dot
 *      (or from the dot down to a target rail).
 *
 * SVG fill/stroke values are hex strings resolved via the theme palette;
 * raw Tailwind classes do not work inside `stroke=`.
 */
export function Rails({ row, prevRow, railWidth, maxRails, laneColors }: RailsProps) {
  // Background color for the commit dot ring — matches the surface the row
  // is mounted on so the dot reads as "popped out" on every preset.
  const background = useThemeColor('background');

  const w = maxRails * railWidth;
  const h = ROW_HEIGHT;
  const cy = h / 2;
  const rx = (rail: number) => rail * railWidth + railWidth / 2;
  const color = (rail: number) => pickLaneColor(laneColors, rail);

  const commitX = rx(row.rail);

  const activeAbove = new Set<number>();
  if (prevRow) {
    for (let r = 0; r < prevRow.rails.length; r++) {
      if (prevRow.rails[r] !== null) activeAbove.add(r);
    }
  }
  const activeBelow = new Set<number>();
  for (let r = 0; r < row.rails.length; r++) {
    if (row.rails[r] !== null) activeBelow.add(r);
  }

  const passThroughRails = Array.from(activeAbove).filter(
    (r) => r !== row.rail && activeBelow.has(r),
  );
  const endingRails = Array.from(activeAbove).filter(
    (r) => r !== row.rail && !activeBelow.has(r),
  );
  const forkEdges = row.edges.filter((e) => e.type === 'fork-out');
  const mergeEdges = row.edges.filter((e) => e.type === 'merge-in');

  return (
    <svg
      width={w}
      height={h}
      viewBox={`0 0 ${w} ${h}`}
      className="shrink-0"
      aria-hidden="true"
    >
      {passThroughRails.map((r) => {
        const x = rx(r);
        return (
          <line
            key={`pt-${r}`}
            x1={x}
            y1={0}
            x2={x}
            y2={h}
            stroke={color(r)}
            strokeWidth={2}
            strokeOpacity={0.6}
          />
        );
      })}

      {activeAbove.has(row.rail) && (
        <line
          x1={commitX}
          y1={0}
          x2={commitX}
          y2={cy}
          stroke={color(row.rail)}
          strokeWidth={2}
          strokeOpacity={0.6}
        />
      )}

      {activeBelow.has(row.rail) && (
        <line
          x1={commitX}
          y1={cy}
          x2={commitX}
          y2={h}
          stroke={color(row.rail)}
          strokeWidth={2}
          strokeOpacity={0.6}
        />
      )}

      {forkEdges.map((edge, i) => (
        <path
          key={`f-${i}`}
          d={`M${rx(edge.fromRail)},${cy} C${rx(edge.fromRail)},${h} ${rx(edge.toRail)},${cy} ${rx(edge.toRail)},${h}`}
          stroke={edge.color}
          strokeWidth={2}
          strokeOpacity={0.6}
          fill="none"
        />
      ))}

      {mergeEdges.map((edge, i) => {
        const isOutgoing = edge.fromRail === row.rail;
        const x1 = rx(edge.fromRail);
        const x2 = rx(edge.toRail);
        const d = isOutgoing
          ? `M${x1},${cy} C${x1},${h} ${x2},${cy} ${x2},${h}`
          : `M${x1},${0} C${x1},${cy} ${x2},${0} ${x2},${cy}`;
        return (
          <path
            key={`m-${i}`}
            d={d}
            stroke={edge.color}
            strokeWidth={2}
            strokeOpacity={0.6}
            fill="none"
          />
        );
      })}

      {endingRails.map((r) => {
        const x = rx(r);
        return (
          <line
            key={`end-${r}`}
            x1={x}
            y1={0}
            x2={x}
            y2={cy}
            stroke={color(r)}
            strokeWidth={2}
            strokeOpacity={0.6}
          />
        );
      })}

      <circle
        cx={commitX}
        cy={cy}
        r={5}
        fill={color(row.rail)}
        stroke={background}
        strokeWidth={2}
      />
    </svg>
  );
}

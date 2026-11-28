// Adapted from jalcoui (MIT) — github.com/jal-co/ui

import type * as React from 'react';

/**
 * Single day entry in the contribution heatmap.
 */
export interface ActivityEntry {
  /** ISO date string (YYYY-MM-DD). */
  date: string;
  /** Activity count for this date. */
  count: number;
}

/**
 * Five opacity stops applied to the resolved theme `primary` color for
 * intensity levels 0–4. Level 0 is the empty / no-activity surface and is
 * intentionally low (almost equal to `bg-muted`).
 *
 * Audit notes (AUDIT.md §1) collapse the full emerald scale to
 * `alpha(primary, …)`, so the same five stops cover light and dark themes.
 */
export const DEFAULT_INTENSITY_OPACITY: readonly [number, number, number, number, number] = [
  0.08, 0.18, 0.35, 0.6, 0.95,
] as const;

/**
 * Thresholds (ratios of `value / max`) that map a normalized count into
 * one of four non-zero intensity buckets. Combined with the empty bucket
 * for `count === 0` they yield the 5 levels expected by the heatmap.
 *
 * Mirrors the original jalcoui `getIntensity` (`<=0.25 / 0.5 / 0.75`).
 */
export const DEFAULT_INTENSITY_THRESHOLDS: readonly [number, number, number] = [0.25, 0.5, 0.75];

export interface ActivityGraphProps extends Omit<React.ComponentProps<'div'>, 'children'> {
  /** Activity data entries. Duplicates with the same `date` are summed. */
  data: ActivityEntry[];
  /**
   * Override the 5 opacity stops applied to the active theme `primary`
   * color. Index 0 is the empty surface; index 4 is the peak.
   */
  intensityOpacity?: readonly [number, number, number, number, number];
  /**
   * Fixed cell size in pixels. When omitted the component auto-sizes
   * blocks to fill the available container width via `useResizeObserver`.
   */
  blockSize?: number;
  /** Cell border radius in pixels. @default 2 */
  blockRadius?: number;
  /** Number of trailing weeks to display. @default 52 */
  weeks?: number;
}

export const GAP = 2;
export const DAY_LABEL_WIDTH = 28;
export const MONTH_LABEL_HEIGHT = 16;
export const DAY_LABELS = ['Mon', 'Wed', 'Fri'] as const;
export const DAY_LABEL_INDICES = [1, 3, 5] as const;
/** `DAY_LABELS` zipped with `DAY_LABEL_INDICES`; keeps the pairing typed at the row level. */
export const DAY_LABEL_ROWS = [
  { label: DAY_LABELS[0], row: DAY_LABEL_INDICES[0] },
  { label: DAY_LABELS[1], row: DAY_LABEL_INDICES[1] },
  { label: DAY_LABELS[2], row: DAY_LABEL_INDICES[2] },
] as const;

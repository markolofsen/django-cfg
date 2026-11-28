// Adapted from jalcoui (MIT) — github.com/jal-co/ui

import type * as React from 'react';

/**
 * Semantic color token name used for the sparkline stroke / area fill.
 *
 * Resolves at runtime via `useThemeColor(color)` from
 * `@djangocfg/ui-core/styles/palette`, so it follows the active theme preset
 * — never reference raw Tailwind scales (`emerald-500`, `sky-400`, …).
 */
export type SparklineColor =
  | 'primary'
  | 'success'
  | 'warning'
  | 'destructive'
  | 'info';

/**
 * Sparkline chart variant.
 *
 *  - `line` — just the stroke.
 *  - `area` — stroke + alpha-filled area underneath.
 *  - `bar`  — discrete bars per data point.
 */
export type SparklineVariant = 'line' | 'area' | 'bar';

/**
 * A datum is either a bare number or an `{ value, label? }` object. The
 * optional `label` is used for `aria-label` enrichment only — it never renders
 * inside the SVG.
 */
export type SparklineDatum = number | { value: number; label?: string };

export interface SparklineProps
  extends Omit<React.ComponentProps<'div'>, 'children'> {
  /** Data points. Empty array renders nothing. */
  data: SparklineDatum[];
  /** Sparkline chart variant. @default 'line' */
  variant?: SparklineVariant;
  /**
   * Semantic color token. Resolved via `useThemeColor()` — respects the
   * active theme preset. @default 'primary'
   */
  color?: SparklineColor;
  /** SVG width in pixels. @default 120 */
  width?: number;
  /** SVG height in pixels. @default 32 */
  height?: number;
  /** Line stroke width (ignored for `bar`). @default 1.5 */
  strokeWidth?: number;
  /** Show a filled dot at the latest data point. @default true */
  showEndpoint?: boolean;
  /** Show a faint dashed line at the average value. @default false */
  showBaseline?: boolean;
  /** Optional accessible label for the chart. */
  ariaLabel?: string;
}

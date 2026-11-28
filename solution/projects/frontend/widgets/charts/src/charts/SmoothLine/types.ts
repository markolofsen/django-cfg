// SmoothLine — streaming sibling of Sparkline.
//
// Drawn on a CANVAS: a single wall-clock rAF loop redraws the whole line each
// frame at its scrolled X (one writer, one clock — the Smoothie/uPlot model), so
// the trace SCROLLS left at constant velocity with no SVG-era path/transform
// desync. Theme-color via the same token bridge as Sparkline.

import type * as React from 'react';

/**
 * Color source for the stroke / area fill.
 *
 *  - A semantic token (`'primary' | 'success' | …`) resolves at runtime via
 *    `useThemeColor()` from `@djangocfg/ui-core/styles/palette`.
 *  - The literal `'currentColor'` is the **token bridge**: the SVG inherits the
 *    CSS `color` of an ancestor, so a host can tint via a `text-*` className
 *    (e.g. cmdop's `text-chart-3`) without going through the semantic set.
 */
export type SmoothLineColor =
  | 'primary'
  | 'success'
  | 'warning'
  | 'destructive'
  | 'info'
  | 'currentColor';

/**
 * Options for {@link useSmoothSeries} (canvas engine). The seed cadence, the
 * scroll toggle, and the right-edge delay.
 */
export interface SmoothSeriesOptions {
  /**
   * Seed cadence (ms) — the first-frame guess + clamp band for the MEASURED
   * scroll velocity, NOT a fixed slide speed. The engine EMAs the real
   * inter-sample interval and drives the scroll off that, so a jittery feed still
   * glides steadily. Stats charts tick ≈ 1000; the quality series (~30 s cadence)
   * wants a longer window. @default 1000
   */
  tweenMs?: number;
  /**
   * Continuous left-scroll: the canvas redraws the whole trace each frame at its
   * wall-clock-scrolled X (a hospital-monitor slide) instead of teleporting. Set
   * for live windowed charts (ECG / traffic). @default false
   */
  scroll?: boolean;
  /**
   * Hold the right edge back by one interval (Smoothie / chartjs-streaming
   * `delay`) so the newest point is known before it scrolls into view — a
   * continuous right edge instead of "grow then snap". The off-edge point is
   * clipped for free by the per-frame `clearRect`. Requires `scroll`.
   * @default true
   */
  delay?: boolean;
}

export interface SmoothLineProps
  extends Omit<React.ComponentProps<'div'>, 'children'> {
  /** Series values, oldest-first. Empty renders a flat baseline. */
  values: readonly number[];
  /**
   * Color token. A semantic token resolves via `useThemeColor()`; `'currentColor'`
   * inherits the ancestor `text-*` tint (the cmdop bridge). @default 'primary'
   */
  color?: SmoothLineColor;
  /** Logical chart width (CSS px). The canvas stretches to its container. @default 240 */
  width?: number;
  /** Logical chart height in CSS px. @default 40 */
  height?: number;
  /** Line stroke width. @default 1.5 */
  strokeWidth?: number;
  /** Render an alpha area fill under the line. @default false */
  area?: boolean;
  /** Wall-clock interval per slot (ms) — the scroll cadence. @default 1000 */
  tweenMs?: number;
  /** Continuous constant-velocity left-scroll for live windowed data. @default false */
  scroll?: boolean;
  /** One-interval right-edge lag (requires `scroll`). @default true */
  delay?: boolean;
  /**
   * Curve smoothness (the line SHAPE, not the motion). The line is drawn as a
   * MONOTONE-CUBIC curve (Fritsch–Carlson / d3 `curveMonotoneX`) through the
   * points so it flows in gentle curves WITHOUT overshooting or inventing values
   * between data points.
   *
   *  - `0`   → straight `L` segments (the angular sparkline look) — the disable
   *    path for charts that need SHARP geometry (e.g. ECG QRS spikes, which
   *    keep their own bespoke builder rather than this generic one).
   *  - any value > 0 → the monotone flowing curve (the default). Monotone-cubic
   *    has no tension parameter of its own, so values above 0 all select the
   *    same non-overshooting curve.
   *
   * This is pure geometry: the curve is rebuilt from the true points once per
   * data change, then the whole trace scrolls. @default 0.5
   */
  tension?: number;
  /** Optional accessible label. */
  ariaLabel?: string;
}

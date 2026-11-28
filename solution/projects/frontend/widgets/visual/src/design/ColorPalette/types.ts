// Adapted from jalcoui (MIT) — github.com/jal-co/ui

import type * as React from 'react';

/**
 * Display format for the copied / rendered color value.
 *
 * - `hex` — `#0989aa` (default). Canvas2D / SVG friendly.
 * - `rgb` — `rgb(9, 137, 170)`.
 * - `hsl` — `hsl(192, 90%, 35%)`.
 */
export type ColorFormat = 'hex' | 'rgb' | 'hsl';

/**
 * A single color entry rendered as one swatch.
 *
 * `value` is always a hex string (`#rrggbb`). Resolve theme tokens
 * to hex via `useThemeColor(...)` before passing them in.
 */
export interface ColorEntry {
  /** Display name (e.g. "Primary", "Success", "brand-accent"). */
  name: string;
  /** Hex color value, e.g. `#0989aa`. */
  value: string;
  /** Optional usage note. */
  description?: string;
}

/**
 * Source of swatches.
 *
 * - `theme` — semantic tokens from `useThemePalette()` (background,
 *   foreground, primary, secondary, muted, accent, destructive, …).
 * - `preset` — status preset family from `useStylePresets()`
 *   (primary, success, warning, danger, info, chart3-5).
 * - `custom` — caller-provided `colors` array.
 */
export type ColorPaletteMode = 'theme' | 'preset' | 'custom';

export interface ColorPaletteProps
  extends Omit<React.ComponentProps<'div'>, 'children'> {
  /**
   * Where swatches come from. Defaults to `'custom'` when `colors` is
   * provided, otherwise `'theme'`.
   */
  mode?: ColorPaletteMode;
  /**
   * Explicit list of swatches (required when `mode === 'custom'`).
   * Ignored for `'theme'` / `'preset'`.
   */
  colors?: ColorEntry[];
  /** Grid column count. @default 4 */
  columns?: number;
  /**
   * Format of the copied value AND the rendered value text.
   * @default 'hex'
   */
  copyFormat?: ColorFormat;
  /** Show the color name label below the swatch. @default true */
  showName?: boolean;
  /** Show the color value string below the swatch. @default true */
  showValue?: boolean;
}

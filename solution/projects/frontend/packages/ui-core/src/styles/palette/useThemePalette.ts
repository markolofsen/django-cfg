'use client';

/**
 * Hook to get theme colors from CSS variables
 *
 * Reads colors directly from document, converting HSL to hex for compatibility
 * with Canvas, SVG, Mermaid, and other tools that don't support CSS variables.
 *
 * **Contrast / semantic pairs:** Filled surfaces (`primary`, `secondary`, `destructive`, …) and
 * their `*-foreground` text colors are defined together in `theme/light.css` and `theme/dark.css`.
 * Components should use `bg-primary text-primary-foreground`, not pick a one-off text color.
 * To change how buttons read, adjust those CSS variables — not per-component styles or hooks.
 *
 * @module ui-core/styles/palette/useThemePalette
 */

import { useMemo } from 'react';
import { useResolvedTheme } from '../../hooks';
import { hslToHex } from './utils';
import type { ThemePalette, StylePresets, BoxColors } from './types';

/**
 * SSR-safe fallback palette (light theme defaults).
 * Used when document is not available (server-side rendering).
 */
const SSR_FALLBACK: Record<string, string> = {
  'background':           '#f5f5f5',
  'foreground':           '#171717',
  'card':                 '#ffffff',
  'card-foreground':      '#171717',
  'popover':              '#ffffff',
  'popover-foreground':   '#171717',
  'muted':                '#e5e5e5',
  'muted-foreground':     '#737373',
  'border':               '#e5e5e5',
  'input':                '#e5e5e5',
  'ring':                 '#0989aa',
  'primary':              '#0989aa',
  'primary-foreground':   '#ffffff',
  'secondary':            '#f5f5f5',
  'secondary-foreground': '#171717',
  'accent':               '#eaf7fa',
  'accent-foreground':    '#171717',
  'destructive':          '#ef4444',
  'destructive-foreground': '#ffffff',
  'chart-1':              '#0989aa',
  'chart-2':              '#22c55e',
  'chart-3':              '#8b5cf6',
  'chart-4':              '#f59e0b',
  'chart-5':              '#ef4444',
};

/**
 * Read a CSS variable from document and convert to hex.
 * Falls back to SSR_FALLBACK on the server.
 */
function getCssColorAsHex(varName: string): string {
  if (typeof document === 'undefined') {
    return SSR_FALLBACK[varName] ?? '#000000';
  }

  const style = getComputedStyle(document.documentElement);
  const value = style.getPropertyValue(`--${varName}`).trim();

  if (!value) return SSR_FALLBACK[varName] ?? '#000000';

  // If already hex, return as-is
  if (value.startsWith('#')) return value;

  // Convert HSL to hex
  return hslToHex(value);
}


/**
 * Convert a hex color to rgba string with given opacity.
 * Works with any hex returned from ThemePalette.
 *
 * @example
 * const palette = useThemePalette();
 * ctx.fillStyle = alpha(palette.primary, 0.3);
 */
export function alpha(hexColor: string, opacity: number): string {
  const hex = hexColor.replace('#', '');
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

/**
 * Hook to get the full theme palette from CSS variables.
 * Returns hex colors for use in Canvas, SVG, Mermaid, and inline styles.
 *
 * @example
 * const palette = useThemePalette();
 * ctx.fillStyle = palette.primary;
 * ctx.fillStyle = alpha(palette.primary, 0.3);
 */
export function useThemePalette(): ThemePalette {
  const theme = useResolvedTheme();

  return useMemo(() => {
    // `theme` is read here so the dependency is real to the linter as well as to
    // us: every getCssColorAsHex call below resolves against the live DOM, whose
    // values change when the theme flips, but nothing in that call chain
    // mentions `theme`. Without this read the memo looks free of it and would be
    // cached across a theme change, returning the previous theme's colors.
    void theme;

    return {
      // Base colors
      background: getCssColorAsHex('background'),
      foreground: getCssColorAsHex('foreground'),
      card: getCssColorAsHex('card'),
      cardForeground: getCssColorAsHex('card-foreground'),
      popover: getCssColorAsHex('popover'),
      popoverForeground: getCssColorAsHex('popover-foreground'),
      muted: getCssColorAsHex('muted'),
      mutedForeground: getCssColorAsHex('muted-foreground'),
      border: getCssColorAsHex('border'),
      input: getCssColorAsHex('input'),
      ring: getCssColorAsHex('ring'),

      // Semantic colors
      primary: getCssColorAsHex('primary'),
      primaryForeground: getCssColorAsHex('primary-foreground'),
      secondary: getCssColorAsHex('secondary'),
      secondaryForeground: getCssColorAsHex('secondary-foreground'),
      accent: getCssColorAsHex('accent'),
      accentForeground: getCssColorAsHex('accent-foreground'),
      destructive: getCssColorAsHex('destructive'),
      destructiveForeground: getCssColorAsHex('destructive-foreground'),

      // Status colors (mapped from chart colors)
      success: getCssColorAsHex('chart-2'), // Green
      successForeground: '#ffffff',
      warning: getCssColorAsHex('chart-4'), // Orange
      warningForeground: '#ffffff',
      info: getCssColorAsHex('chart-1'), // Brand / primary hue
      infoForeground: '#ffffff',

      // Chart colors
      chart1: getCssColorAsHex('chart-1'),
      chart2: getCssColorAsHex('chart-2'),
      chart3: getCssColorAsHex('chart-3'),
      chart4: getCssColorAsHex('chart-4'),
      chart5: getCssColorAsHex('chart-5'),
    };
  }, [theme]);
}

/**
 * Hook to get style presets for elements (nodes, boxes, etc.)
 *
 * @example
 * ```tsx
 * function MyDiagram() {
 *   const presets = useStylePresets();
 *
 *   // Use in Mermaid FlowDiagram
 *   flow.style.define('success', presets.success);
 *   flow.style.define('primary', presets.primary);
 * }
 * ```
 */
export function useStylePresets(): StylePresets {
  const palette = useThemePalette();

  return useMemo(() => ({
    primary: {
      fill: palette.primary,
      stroke: palette.primary,
      color: palette.primaryForeground,
    },
    secondary: {
      fill: palette.secondary,
      stroke: palette.secondary,
      color: palette.secondaryForeground,
    },
    success: {
      fill: palette.success,
      stroke: palette.success,
      color: palette.successForeground,
    },
    danger: {
      fill: palette.destructive,
      stroke: palette.destructive,
      color: palette.destructiveForeground,
    },
    warning: {
      fill: palette.warning,
      stroke: palette.warning,
      color: palette.warningForeground,
    },
    info: {
      fill: palette.info,
      stroke: palette.info,
      color: palette.infoForeground,
    },
    muted: {
      fill: palette.muted,
      stroke: palette.border,
      color: palette.mutedForeground,
    },
    card: {
      fill: palette.card,
      stroke: palette.border,
      color: palette.cardForeground,
    },
    accent: {
      fill: palette.accent,
      stroke: palette.border,
      color: palette.accentForeground,
    },
    chart1: {
      fill: palette.chart1,
      stroke: palette.chart1,
      color: palette.primaryForeground,
    },
    chart2: {
      fill: palette.chart2,
      stroke: palette.chart2,
      color: palette.primaryForeground,
    },
    chart3: {
      fill: palette.chart3,
      stroke: palette.chart3,
      color: palette.primaryForeground,
    },
    chart4: {
      fill: palette.chart4,
      stroke: palette.chart4,
      color: palette.primaryForeground,
    },
    chart5: {
      fill: palette.chart5,
      stroke: palette.chart5,
      color: palette.primaryForeground,
    },
  }), [palette]);
}

/**
 * Hook to get box/region colors (e.g., for Mermaid rect blocks)
 *
 * @example
 * ```tsx
 * function MySequenceDiagram() {
 *   const boxes = useBoxColors();
 *
 *   // Use in Mermaid SequenceDiagram
 *   rect(boxes.primary, () => {
 *     d.Alice.sync.Bob.msg('Hello');
 *   });
 * }
 * ```
 */
export function useBoxColors(): BoxColors {
  const theme = useResolvedTheme();
  const palette = useThemePalette();

  return useMemo(() => {
    const opacity = theme === 'dark' ? 0.3 : 0.15;

    return {
      primary: alpha(palette.primary, opacity),
      success: alpha(palette.success, opacity),
      warning: alpha(palette.warning, opacity),
      danger: alpha(palette.destructive, opacity),
      info: alpha(palette.info, opacity),
      muted: alpha(palette.muted, opacity),
    };
  }, [theme, palette]);
}

/**
 * Hook to get a single theme color by CSS variable name.
 * Lighter alternative to useThemePalette() when you only need 1-3 colors.
 *
 * @param varName - CSS variable name without `--` prefix (e.g. 'primary', 'card-foreground')
 * @param opacity - Optional opacity 0-1. If provided, returns rgba() string instead of hex.
 *
 * @example
 * // Hex color
 * const primary = useThemeColor('primary');           // '#a855f7'
 *
 * // With opacity
 * const wave = useThemeColor('primary', 0.3);         // 'rgba(168, 85, 247, 0.3)'
 * const bg   = useThemeColor('destructive', 0.1);     // useful for error backgrounds
 */
export function useThemeColor(varName: string, opacity?: number): string {
  const theme = useResolvedTheme();

  return useMemo(() => {
    const hex = getCssColorAsHex(varName);
    return opacity !== undefined ? alpha(hex, opacity) : hex;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [theme, varName, opacity]);
}

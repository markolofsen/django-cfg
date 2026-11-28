/**
 * Theme Palette Types
 * @module ui-core/styles/palette/types
 */

/**
 * Complete semantic color palette for programmatic use
 * (Canvas, SVG, Mermaid diagrams, etc.)
 */
export interface ThemePalette {
  // Base Colors
  background: string;
  foreground: string;
  card: string;
  cardForeground: string;
  popover: string;
  popoverForeground: string;
  muted: string;
  mutedForeground: string;
  border: string;
  input: string;
  ring: string;

  // Semantic Colors
  primary: string;
  primaryForeground: string;
  secondary: string;
  secondaryForeground: string;
  accent: string;
  accentForeground: string;
  destructive: string;
  destructiveForeground: string;

  // Status Colors
  success: string;
  successForeground: string;
  warning: string;
  warningForeground: string;
  info: string;
  infoForeground: string;

  // Chart Colors
  chart1: string;
  chart2: string;
  chart3: string;
  chart4: string;
  chart5: string;
}

/**
 * Style colors for elements (fill, stroke, text)
 */
export interface StyleColors {
  fill: string;
  stroke: string;
  color: string;
}

/**
 * Style presets for common UI patterns
 */
export interface StylePresets {
  primary: StyleColors;
  secondary: StyleColors;
  success: StyleColors;
  danger: StyleColors;
  warning: StyleColors;
  info: StyleColors;
  muted: StyleColors;
  card: StyleColors;
  accent: StyleColors;
  chart1: StyleColors;
  chart2: StyleColors;
  chart3: StyleColors;
  chart4: StyleColors;
  chart5: StyleColors;
}

/**
 * Background colors for boxes/regions
 * (e.g., Mermaid rect blocks, highlighted sections)
 */
export interface BoxColors {
  primary: string;
  success: string;
  warning: string;
  danger: string;
  info: string;
  muted: string;
}

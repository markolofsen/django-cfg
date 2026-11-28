/**
 * Theme Palette
 *
 * Hooks and utilities for accessing theme colors programmatically.
 * Colors are read directly from CSS variables, ensuring consistency
 * with the theme system.
 *
 * @example
 * ```tsx
 * import {
 *   useThemePalette,
 *   useStylePresets,
 *   useBoxColors
 * } from '@djangocfg/ui-core/styles/palette';
 *
 * function MyComponent() {
 *   const palette = useThemePalette();
 *   const presets = useStylePresets();
 *   const boxes = useBoxColors();
 *
 *   // Use in canvas
 *   ctx.fillStyle = palette.primary;
 *
 *   // Use in Mermaid FlowDiagram
 *   flow.style.define('success', presets.success);
 *
 *   // Use in Mermaid SequenceDiagram rect
 *   rect(boxes.primary, () => { ... });
 * }
 * ```
 *
 * @module ui-core/styles/palette
 */

// Types
export type {
  ThemePalette,
  StyleColors,
  StylePresets,
  BoxColors,
} from './types';

// Hooks
export {
  useThemePalette,
  useStylePresets,
  useBoxColors,
  useThemeColor,
  alpha,
} from './useThemePalette';

// Utils (for advanced use)
export {
  hslToHex,
  hslToRgbString,
  hslToRgba,
} from './utils';

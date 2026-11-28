/**
 * Theme utilities for Mermaid builders
 *
 * Re-exports palette hooks from @djangocfg/ui-core for convenience.
 *
 * @example
 * ```tsx
 * import { useStylePresets, useBoxColors } from './theme';
 *
 * function MyDiagram() {
 *   const presets = useStylePresets();
 *   const boxes = useBoxColors();
 *
 *   const flow = FlowDiagram();
 *   flow.style.define('success', presets.success);
 *
 *   const { rect } = SequenceDiagram({ ... });
 *   rect(boxes.primary, () => { ... });
 * }
 * ```
 *
 * @module Mermaid/builders/core/theme
 */

// Re-export from ui-core palette
export {
  // Types
  type ThemePalette,
  type StyleColors,
  type StylePresets,
  type BoxColors,

  // Hooks
  useThemePalette,
  useStylePresets,
  useBoxColors,

  // Utils
  hslToHex,
  hslToRgbString,
  hslToRgba,
} from '@djangocfg/ui-core/styles/palette';

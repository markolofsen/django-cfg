// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// Grid of color swatches with click-to-copy in hex / rgb / hsl.
// Pulls colors from one of three sources via `mode`:
//   - 'theme'  → useThemePalette() (semantic tokens of the active theme)
//   - 'preset' → useStylePresets() (status preset families)
//   - 'custom' → caller-provided `colors` array
//
// Chrome (frame, value label) uses semantic Tailwind tokens; the swatch
// background uses inline `style={{ backgroundColor: hex }}` so it stays
// honest regardless of the active theme. See CONTRACT.md §2/§3.

'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { useThemePalette, useStylePresets } from '@djangocfg/ui-core/styles/palette';
import { Swatch } from './components/Swatch';
import type { ColorEntry, ColorPaletteMode, ColorPaletteProps } from './types';

function resolveMode(
  mode: ColorPaletteMode | undefined,
  colors: ColorEntry[] | undefined,
): ColorPaletteMode {
  if (mode) return mode;
  return colors && colors.length > 0 ? 'custom' : 'theme';
}

/**
 * Build the swatch list for `mode === 'theme'` — semantic tokens of the
 * current theme. Includes the foreground/background pair plus brand and
 * status families so a docs page can show "what does this preset look
 * like" at a glance.
 */
function useThemeEntries(): ColorEntry[] {
  const palette = useThemePalette();
  return React.useMemo<ColorEntry[]>(
    () => [
      { name: 'Background', value: palette.background },
      { name: 'Foreground', value: palette.foreground },
      { name: 'Card', value: palette.card },
      { name: 'Muted', value: palette.muted },
      { name: 'Muted Foreground', value: palette.mutedForeground },
      { name: 'Border', value: palette.border },
      { name: 'Primary', value: palette.primary },
      { name: 'Secondary', value: palette.secondary },
      { name: 'Accent', value: palette.accent },
      { name: 'Destructive', value: palette.destructive },
      { name: 'Success', value: palette.success },
      { name: 'Warning', value: palette.warning },
      { name: 'Info', value: palette.info },
    ],
    [palette],
  );
}

/**
 * Build the swatch list for `mode === 'preset'` — the status / brand
 * families exposed by `useStylePresets()`. Renders the `fill` color
 * for each preset; consumers needing stroke/foreground should query
 * the preset hooks directly.
 */
function usePresetEntries(): ColorEntry[] {
  const presets = useStylePresets();
  return React.useMemo<ColorEntry[]>(
    () => [
      { name: 'Primary', value: presets.primary.fill },
      { name: 'Success', value: presets.success.fill },
      { name: 'Warning', value: presets.warning.fill },
      { name: 'Danger', value: presets.danger.fill },
      { name: 'Info', value: presets.info.fill },
      { name: 'Chart 3', value: presets.chart3.fill },
      { name: 'Chart 4', value: presets.chart4.fill },
      { name: 'Chart 5', value: presets.chart5.fill },
    ],
    [presets],
  );
}

export function ColorPalette({
  mode,
  colors,
  columns = 4,
  copyFormat = 'hex',
  showName = true,
  showValue = true,
  className,
  style,
  ...rest
}: ColorPaletteProps) {
  // Always call both hooks so React keeps a stable order regardless of `mode`.
  const themeEntries = useThemeEntries();
  const presetEntries = usePresetEntries();

  const resolvedMode = resolveMode(mode, colors);
  const entries = React.useMemo<ColorEntry[]>(() => {
    if (resolvedMode === 'theme') return themeEntries;
    if (resolvedMode === 'preset') return presetEntries;
    return colors ?? [];
  }, [resolvedMode, themeEntries, presetEntries, colors]);

  const gridStyle = React.useMemo<React.CSSProperties>(
    () => ({
      ...style,
      gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))`,
    }),
    [style, columns],
  );

  return (
    <div
      data-slot="color-palette"
      data-mode={resolvedMode}
      className={cn('grid gap-3', className)}
      style={gridStyle}
      {...rest}
    >
      {entries.map((color) => (
        <Swatch
          key={`${color.name}-${color.value}`}
          color={color}
          copyFormat={copyFormat}
          showName={showName}
          showValue={showValue}
        />
      ))}
    </div>
  );
}

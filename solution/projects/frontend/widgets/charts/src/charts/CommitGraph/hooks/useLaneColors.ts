// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import { useMemo } from 'react';
import { useStylePresets } from '@djangocfg/ui-core/styles/palette';

/**
 * Hook returning the categorical lane palette as an array of hex strings.
 *
 * jalcoui hard-codes 8 raw colors (`#3b82f6`, `#22c55e`, …) — that would
 * break every non-default theme preset. We instead derive the palette from
 * {@link useStylePresets}: 8 distinguishable categorical fills that already
 * respect the active theme. Branches beyond index 7 cycle modulo the
 * palette length.
 *
 * Order is chosen for maximum perceptual distance between adjacent rails:
 * primary → success → warning → danger → info → chart3 → chart4 → chart5.
 */
export function useLaneColors(): string[] {
  const presets = useStylePresets();

  return useMemo(
    () => [
      presets.primary.fill,
      presets.success.fill,
      presets.warning.fill,
      presets.danger.fill,
      presets.info.fill,
      presets.chart3.fill,
      presets.chart4.fill,
      presets.chart5.fill,
    ],
    [presets],
  );
}

/**
 * Pick the color for a rail index, cycling when there are more rails than
 * palette entries.
 */
export function pickLaneColor(colors: string[], rail: number): string {
  if (colors.length === 0) return '#000000';
  // Modulo is normalised into range above, so the read always hits.
  return colors[((rail % colors.length) + colors.length) % colors.length] ?? '#000000';
}

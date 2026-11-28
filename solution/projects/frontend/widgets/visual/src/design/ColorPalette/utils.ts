// Adapted from jalcoui (MIT) — github.com/jal-co/ui

import type { ColorFormat } from './types';

/**
 * Parse a `#rrggbb` / `#rgb` hex string into `{ r, g, b }` (0–255).
 * Returns `null` for malformed input.
 */
function parseHex(hex: string): { r: number; g: number; b: number } | null {
  const cleaned = hex.trim().replace(/^#/, '');
  if (cleaned.length === 3) {
    const [c0, c1, c2] = cleaned;
    if (c0 === undefined || c1 === undefined || c2 === undefined) return null;
    const r = parseInt(c0 + c0, 16);
    const g = parseInt(c1 + c1, 16);
    const b = parseInt(c2 + c2, 16);
    if ([r, g, b].some(Number.isNaN)) return null;
    return { r, g, b };
  }
  if (cleaned.length === 6) {
    const r = parseInt(cleaned.slice(0, 2), 16);
    const g = parseInt(cleaned.slice(2, 4), 16);
    const b = parseInt(cleaned.slice(4, 6), 16);
    if ([r, g, b].some(Number.isNaN)) return null;
    return { r, g, b };
  }
  return null;
}

function rgbToHsl(
  r: number,
  g: number,
  b: number,
): { h: number; s: number; l: number } {
  const rn = r / 255;
  const gn = g / 255;
  const bn = b / 255;
  const max = Math.max(rn, gn, bn);
  const min = Math.min(rn, gn, bn);
  const l = (max + min) / 2;
  let h = 0;
  let s = 0;
  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case rn:
        h = (gn - bn) / d + (gn < bn ? 6 : 0);
        break;
      case gn:
        h = (bn - rn) / d + 2;
        break;
      case bn:
        h = (rn - gn) / d + 4;
        break;
    }
    h /= 6;
  }
  return { h: Math.round(h * 360), s: Math.round(s * 100), l: Math.round(l * 100) };
}

/**
 * Format a hex color into the requested {@link ColorFormat}. Falls
 * back to the original string when the hex is unparseable.
 */
export function formatColor(hex: string, format: ColorFormat): string {
  if (format === 'hex') return hex.toLowerCase();
  const rgb = parseHex(hex);
  if (!rgb) return hex;
  if (format === 'rgb') return `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`;
  const { h, s, l } = rgbToHsl(rgb.r, rgb.g, rgb.b);
  return `hsl(${h}, ${s}%, ${l}%)`;
}

/**
 * WCAG relative luminance — the same formula `ui-core`'s preset-contrast gate
 * uses (`scripts/check-preset-contrast.mjs`), so a swatch and a theme token
 * are judged by one standard.
 *
 * Note the gamma step: sRGB channels are gamma-encoded, and skipping the
 * linearisation is what makes a naive brightness number disagree with what an
 * eye sees.
 */
function relativeLuminance({ r, g, b }: { r: number; g: number; b: number }): number {
  const linear = [r, g, b].map((channel) => {
    const c = channel / 255;
    return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  });
  return (linear[0] ?? 0) * 0.2126 + (linear[1] ?? 0) * 0.7152 + (linear[2] ?? 0) * 0.0722;
}

/**
 * Return `'light'` when black text reads better against the colour than white
 * does, otherwise `'dark'`.
 *
 * **This compares the two actual contrast ratios rather than testing a
 * brightness threshold.** It used to be Rec. 601 luminance against a
 * hard-coded `> 0.6`, which put pure green (`0.587`) on the wrong side: the
 * swatch got white text at **1.37:1**, where black would have given 15.30:1.
 * AA wants 4.5:1, so that was not a near miss — and it took the whole
 * bright-green band and the mid greys with it (`#999999`: 2.85:1 white vs
 * 7.37:1 black).
 *
 * A threshold is a guess at where the crossover sits. The crossover is
 * computable, so compute it.
 */
export function getReadableContrast(hex: string): 'light' | 'dark' {
  const rgb = parseHex(hex);
  if (!rgb) return 'dark';
  const luminance = relativeLuminance(rgb);
  const contrastWithBlack = (luminance + 0.05) / 0.05;
  const contrastWithWhite = 1.05 / (luminance + 0.05);
  return contrastWithBlack >= contrastWithWhite ? 'light' : 'dark';
}

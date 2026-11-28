/**
 * Color conversion utilities
 * @module ui-core/styles/palette/utils
 */

/**
 * Parse HSL string from CSS variable to components.
 * Accepts either the raw triplet form `"192 90% 35%"` or the wrapped
 * form `"hsl(192 90% 35%)"` / `"hsl(192, 90%, 35%)"`. `getComputedStyle`
 * returns the wrapped form when the CSS variable is declared as
 * `--primary: hsl(...)` rather than `--primary: 192 90% 35%`.
 */
function parseHslString(hsl: string): { h: number; s: number; l: number } | null {
  const stripped = hsl
    .trim()
    .replace(/^hsla?\(/i, '')
    .replace(/\)$/, '')
    .replace(/,/g, ' ')
    .replace(/\s*\/\s*[\d.]+%?$/, ''); // drop optional `/ alpha`
  const match = stripped.match(/^(-?\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)%\s+(\d+(?:\.\d+)?)%$/);
  if (!match) return null;
  const hue = match[1];
  const saturation = match[2];
  const lightness = match[3];
  if (hue === undefined || saturation === undefined || lightness === undefined) return null;
  return {
    h: parseFloat(hue),
    s: parseFloat(saturation),
    l: parseFloat(lightness),
  };
}

/**
 * Convert HSL to RGB
 */
function hslToRgb(h: number, s: number, l: number): { r: number; g: number; b: number } {
  s /= 100;
  l /= 100;

  const c = (1 - Math.abs(2 * l - 1)) * s;
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
  const m = l - c / 2;

  let r: number, g: number, b: number;

  if (h >= 0 && h < 60) { r = c; g = x; b = 0; }
  else if (h >= 60 && h < 120) { r = x; g = c; b = 0; }
  else if (h >= 120 && h < 180) { r = 0; g = c; b = x; }
  else if (h >= 180 && h < 240) { r = 0; g = x; b = c; }
  else if (h >= 240 && h < 300) { r = x; g = 0; b = c; }
  else { r = c; g = 0; b = x; }

  return {
    r: Math.round((r + m) * 255),
    g: Math.round((g + m) * 255),
    b: Math.round((b + m) * 255),
  };
}

/**
 * Convert RGB to hex string
 */
function rgbToHex(r: number, g: number, b: number): string {
  const toHex = (n: number) => n.toString(16).padStart(2, '0');
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

/**
 * Convert CSS HSL variable value to hex
 * Input: "15 55% 45%" (from CSS --primary in light theme)
 * Output: "#b25334"
 */
export function hslToHex(hslString: string): string {
  const parsed = parseHslString(hslString);
  if (!parsed) return '#000000';

  const { r, g, b } = hslToRgb(parsed.h, parsed.s, parsed.l);
  return rgbToHex(r, g, b);
}

/**
 * Convert CSS HSL variable value to rgb() string
 * Input: "192 90% 35%"
 * Output: "rgb(59, 130, 246)"
 */
export function hslToRgbString(hslString: string): string {
  const parsed = parseHslString(hslString);
  if (!parsed) return 'rgb(0, 0, 0)';

  const { r, g, b } = hslToRgb(parsed.h, parsed.s, parsed.l);
  return `rgb(${r}, ${g}, ${b})`;
}

/**
 * Convert CSS HSL variable value to rgba() string with opacity
 * Input: "192 90% 35%", 0.2
 * Output: "rgba(59, 130, 246, 0.2)"
 */
export function hslToRgba(hslString: string, alpha: number): string {
  const parsed = parseHslString(hslString);
  if (!parsed) return `rgba(0, 0, 0, ${alpha})`;

  const { r, g, b } = hslToRgb(parsed.h, parsed.s, parsed.l);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

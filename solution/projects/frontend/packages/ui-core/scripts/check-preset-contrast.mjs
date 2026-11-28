import { readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const MINIMUM_TEXT_CONTRAST = 4.5;
const MINIMUM_LIGHT_SURFACE_GAP = 2;
/**
 * An interactive surface must be visibly separated from the surface it sits on,
 * IN BOTH MODES.
 *
 * Added 2026-08-03 after a reported "hover is fine in dark, invisible in light".
 * It was: macOS sidebar 94% with a 93% hover — a ONE-point step, against ELEVEN
 * in dark. Three presets shared the flaw and one (windows) stepped the wrong
 * way entirely, its hover LIGHTER than the rail it highlighted.
 *
 * Every one passed the existing gate, because that gate only ever compared
 * --muted with --background. A rail hover lands on --sidebar-background, which
 * nothing checked. The lesson is in the pair list below: check the surface the
 * user actually sees, not a neighbouring one that happens to be nearby.
 */
const MINIMUM_INTERACTIVE_SURFACE_GAP = 4;
const INTERACTIVE_SURFACE_PAIRS = [
  ["sidebar-accent", "sidebar-background"],
  ["accent", "background"],
];
/**
 * A RESTING surface must not shout. The ceiling, not a floor.
 *
 * Added 2026-08-16 after "таблица сильно контрастная относительно основной
 * темы... не такая кондовая". A table sits on --card, and in the macOS dark
 * preset --card was ELEVEN lightness points above --background (8% -> 15%),
 * with --border seven more on top. Three sharply separated plates, so a table
 * read as a sticker laid over the page rather than part of it.
 *
 * The existing gates could not see it: text pairs check foreground on
 * background, and the interactive-surface gate checks that a HOVER is
 * different ENOUGH. Nobody asked whether a resting surface was different TOO
 * MUCH — which is how seven points shipped.
 *
 * Real macOS separates dark surfaces by two to four points and lets a hairline
 * border finish the job. Four is the ceiling here: past it the fill, not the
 * border, becomes what divides the page, and every nested surface compounds
 * the error.
 *
 * Dark only. A light theme's card is white on grey — a large, correct step
 * that carries elevation the way paper does.
 */
const MAXIMUM_RESTING_SURFACE_GAP = 4;
const RESTING_SURFACE_PAIRS = [["card", "background"]];
/**
 * A hairline divides; it does not glow.
 *
 * Once the fill stopped separating surfaces (above), the BORDER became the
 * loudest thing on a dark page: macOS sat at 22% lightness over an 8%
 * background — measured luminance 0.213 against the card's 0.118, a line
 * almost twice as bright as the surface it edges. That is what remained of
 * "кондово" after the fills were calmed.
 *
 * Ten points is enough to read as a definite edge at one device pixel and not
 * enough to draw the eye before the content does.
 */
const MAXIMUM_BORDER_GAP = 10;
/*
 * --popover is deliberately NOT here, though it fails this ceiling in all
 * seven presets by up to thirteen points. A popover is a FLOATING layer: it
 * has to read as detached from the page it covers. In light mode a shadow does
 * that work, but the dark theme sets `--shadow-card: none` — measured, not
 * assumed — so in the dark its lightness step IS its separation. Capping it
 * would leave a menu with nothing to lift it off the page at all.
 */
/** Contrast IS the product here, so the ceiling does not apply. */
const RESTING_GAP_EXEMPT_PRESETS = new Set(["high-contrast"]);

const TEXT_CONTRAST_PRESET = "macos";
const lightThemePath = fileURLToPath(new URL("../src/styles/css/theme/light.css", import.meta.url));
const darkThemePath = fileURLToPath(new URL("../src/styles/css/theme/dark.css", import.meta.url));
const presetDirectory = fileURLToPath(new URL("../src/styles/css/presets/", import.meta.url));

const PAIRS = [
  ["foreground", "background"],
  ["card-foreground", "card"],
  ["popover-foreground", "popover"],
  ["primary-foreground", "primary"],
  ["secondary-foreground", "secondary"],
  ["accent-foreground", "accent"],
  ["destructive-foreground", "destructive"],
  ["sidebar-foreground", "sidebar-background"],
  ["sidebar-primary-foreground", "sidebar-primary"],
  ["sidebar-accent-foreground", "sidebar-accent"],
  ["muted-foreground", "background"],
  ["muted-foreground", "card"],
  ["muted-foreground", "popover"],
  ["muted-foreground", "muted"],
  ["muted-foreground", "accent"],
  ["warning-foreground", "warning-background"],
  ["success-foreground", "success-background"],
  ["info-foreground", "info-background"],
  ["on-success", "success"],
  ["on-warning", "warning"],
  ["on-info", "info"],
  ["on-destructive", "destructive"],
];

function parseBlocks(css) {
  // Comments in the theme files contain examples such as `--{status}`.
  // Strip them before locating rule braces so those examples cannot truncate
  // a selector block and silently hide declarations from the checker.
  const uncommented = css.replace(/\/\*[\s\S]*?\*\//g, "");
  const result = new Map();
  for (const match of uncommented.matchAll(/(:root|\.dark)\s*\{([\s\S]*?)\}/g)) {
    const tokens = new Map();
    for (const declaration of match[2].matchAll(/--([\w-]+):\s*([^;]+);/g)) {
      tokens.set(declaration[1], declaration[2].trim());
    }
    result.set(match[1], tokens);
  }
  return result;
}

function mergeBlocks(...blockMaps) {
  const result = new Map([
    [":root", new Map()],
    [".dark", new Map()],
  ]);
  for (const blocks of blockMaps) {
    for (const [selector, tokens] of blocks) {
      const target = result.get(selector);
      for (const [token, value] of tokens) target.set(token, value);
    }
  }
  return result;
}

function parseHsl(value, token, mode) {
  const match = value.match(/^hsl\(\s*([\d.]+)\s+([\d.]+)%\s+([\d.]+)%\s*\)$/);
  if (!match) {
    throw new Error(`${mode} --${token} is not an opaque HSL color: ${value}`);
  }
  return match.slice(1).map(Number);
}

function hslToSrgb([hue, saturation, lightness]) {
  const s = saturation / 100;
  const l = lightness / 100;
  const chroma = (1 - Math.abs(2 * l - 1)) * s;
  const x = chroma * (1 - Math.abs(((hue / 60) % 2) - 1));
  const m = l - chroma / 2;
  const [red, green, blue] =
    hue < 60
      ? [chroma, x, 0]
      : hue < 120
        ? [x, chroma, 0]
        : hue < 180
          ? [0, chroma, x]
          : hue < 240
            ? [0, x, chroma]
            : hue < 300
              ? [x, 0, chroma]
              : [chroma, 0, x];
  return [red + m, green + m, blue + m];
}

function relativeLuminance(rgb) {
  const linear = rgb.map((channel) =>
    channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4
  );
  return linear[0] * 0.2126 + linear[1] * 0.7152 + linear[2] * 0.0722;
}

function contrastRatio(foreground, background) {
  const lighter = Math.max(relativeLuminance(foreground), relativeLuminance(background));
  const darker = Math.min(relativeLuminance(foreground), relativeLuminance(background));
  return (lighter + 0.05) / (darker + 0.05);
}

const failures = [];
const baseModes = mergeBlocks(
  parseBlocks(readFileSync(lightThemePath, "utf8")),
  parseBlocks(readFileSync(darkThemePath, "utf8"))
);
const presetFiles = readdirSync(presetDirectory)
  .filter((name) => name.endsWith(".css"))
  .sort();

for (const presetFile of presetFiles) {
  const preset = presetFile.replace(/\.css$/, "");
  const presetModes = parseBlocks(readFileSync(`${presetDirectory}/${presetFile}`, "utf8"));
  const modes = mergeBlocks(baseModes, presetModes);

  for (const [selector, tokens] of modes) {
    const mode = selector === ":root" ? "light" : "dark";
    if (preset === TEXT_CONTRAST_PRESET) {
      for (const [foregroundToken, backgroundToken] of PAIRS) {
        const foregroundValue = tokens.get(foregroundToken);
        const backgroundValue = tokens.get(backgroundToken);
        if (!foregroundValue || !backgroundValue) {
          failures.push(`${preset}/${mode}: missing --${foregroundToken} or --${backgroundToken}`);
          continue;
        }
        const ratio = contrastRatio(
          hslToSrgb(parseHsl(foregroundValue, foregroundToken, `${preset}/${mode}`)),
          hslToSrgb(parseHsl(backgroundValue, backgroundToken, `${preset}/${mode}`))
        );
        const label = `${preset}/${mode} --${foregroundToken} / --${backgroundToken}`;
        console.log(
          `${ratio >= MINIMUM_TEXT_CONTRAST ? "PASS" : "FAIL"} ${ratio.toFixed(2)} ${label}`
        );
        if (ratio < MINIMUM_TEXT_CONTRAST) {
          failures.push(
            `${label} is ${ratio.toFixed(2)}:1; expected at least ${MINIMUM_TEXT_CONTRAST}:1`
          );
        }
      }
    }

    for (const [surfaceToken, baseToken] of INTERACTIVE_SURFACE_PAIRS) {
      const surfaceValue = tokens.get(surfaceToken);
      const baseValue = tokens.get(baseToken);
      // A preset may legitimately inherit either token from theme.css.
      if (!surfaceValue || !baseValue) continue;
      const surface = parseHsl(surfaceValue, surfaceToken, `${preset}/${mode}`);
      const base = parseHsl(baseValue, baseToken, `${preset}/${mode}`);
      // Direction is not asserted: a light theme darkens its hover and a dark
      // theme lightens it. Only the SIZE of the step is a contract, so the two
      // modes do comparable work for the same interaction.
      const gap = Math.abs(surface[2] - base[2]);
      const label = `${preset}/${mode} --${surfaceToken} / --${baseToken} surface gap`;
      console.log(
        `${gap >= MINIMUM_INTERACTIVE_SURFACE_GAP ? "PASS" : "FAIL"} ${gap.toFixed(2)} ${label}`
      );
      if (gap < MINIMUM_INTERACTIVE_SURFACE_GAP) {
        failures.push(
          `${label} is ${gap.toFixed(2)} lightness points; expected at least ${MINIMUM_INTERACTIVE_SURFACE_GAP}`
        );
      }
    }

    if (mode === "dark" && !RESTING_GAP_EXEMPT_PRESETS.has(preset)) {
      for (const [surfaceToken, baseToken] of RESTING_SURFACE_PAIRS) {
        const surfaceValue = tokens.get(surfaceToken);
        const baseValue = tokens.get(baseToken);
        // A preset may legitimately inherit either token from theme.css.
        if (!surfaceValue || !baseValue) continue;
        const surface = parseHsl(surfaceValue, surfaceToken, `${preset}/${mode}`);
        const base = parseHsl(baseValue, baseToken, `${preset}/${mode}`);
        const gap = Math.abs(surface[2] - base[2]);
        const label = `${preset}/${mode} --${surfaceToken} / --${baseToken} resting gap`;
        console.log(
          `${gap <= MAXIMUM_RESTING_SURFACE_GAP ? "PASS" : "FAIL"} ${gap.toFixed(2)} ${label}`
        );
        if (gap > MAXIMUM_RESTING_SURFACE_GAP) {
          failures.push(
            `${label} is ${gap.toFixed(2)} lightness points; expected at most ${MAXIMUM_RESTING_SURFACE_GAP} — a resting surface is separated by its border, not by its fill`
          );
        }
      }
    }

    if (mode === "dark" && !RESTING_GAP_EXEMPT_PRESETS.has(preset)) {
      const borderValue = tokens.get("border");
      const backgroundValue = tokens.get("background");
      if (borderValue && backgroundValue) {
        const border = parseHsl(borderValue, "border", `${preset}/${mode}`);
        const background = parseHsl(backgroundValue, "background", `${preset}/${mode}`);
        const gap = Math.abs(border[2] - background[2]);
        const label = `${preset}/${mode} --border / --background gap`;
        console.log(`${gap <= MAXIMUM_BORDER_GAP ? "PASS" : "FAIL"} ${gap.toFixed(2)} ${label}`);
        if (gap > MAXIMUM_BORDER_GAP) {
          failures.push(
            `${label} is ${gap.toFixed(2)} lightness points; expected at most ${MAXIMUM_BORDER_GAP} — a hairline divides, it does not glow`
          );
        }
      }
    }

    if (mode === "light") {
      const background = parseHsl(tokens.get("background"), "background", `${preset}/${mode}`);
      const muted = parseHsl(tokens.get("muted"), "muted", `${preset}/${mode}`);
      const surfaceGap = background[2] - muted[2];
      const label = `${preset}/${mode} --background / --muted surface gap`;
      console.log(
        `${surfaceGap >= MINIMUM_LIGHT_SURFACE_GAP ? "PASS" : "FAIL"} ${surfaceGap.toFixed(2)} ${label}`
      );
      if (surfaceGap < MINIMUM_LIGHT_SURFACE_GAP) {
        failures.push(
          `${label} is ${surfaceGap.toFixed(2)} lightness points; expected muted to be at least ${MINIMUM_LIGHT_SURFACE_GAP} points darker`
        );
      }
    }
  }
}

if (failures.length > 0) {
  throw new Error(`Theme preset contrast check failed:\n${failures.join("\n")}`);
}

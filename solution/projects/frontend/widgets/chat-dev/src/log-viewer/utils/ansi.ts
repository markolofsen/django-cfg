// Adapted from jalcoui (MIT) — github.com/jal-co/ui

// Minimal ANSI SGR (Select Graphic Rendition) parser.
//
// Scope: 8-color and 16-color (bright) foreground / background codes plus
// the structural codes (`0` reset, `1` bold, `2` dim, `3` italic, `4`
// underline). 256-color and truecolor sequences (`38;5;N`, `38;2;R;G;B`)
// are recognized at the parser level — we step over their parameters so
// they don't corrupt the next span — but we do not honor the exact RGB;
// they fall back to the default foreground. The 16-color palette is more
// than enough for the typical CLI log surface (`chalk`, `consola`,
// `pino-pretty`, …), and we trade fidelity for guaranteed semantic-token
// routing.

import type { LogTone } from '../types';
import { TONE_CLASSES } from '../types';

/** A contiguous text segment with resolved style attributes. */
export interface AnsiSegment {
  text: string;
  /** Resolved tone for color routing — `undefined` means default
   * foreground. */
  tone?: LogTone;
  bold?: boolean;
  dim?: boolean;
  italic?: boolean;
  underline?: boolean;
}

/**
 * Map a raw ANSI SGR color code to a {@link LogTone}. The mapping mirrors
 * the standard chalk-style palette so a log line that says `chalk.red(…)`
 * lights up as `destructive` under every preset.
 *
 * - 30/40 (black)   → muted
 * - 31/41 (red)     → destructive
 * - 32/42 (green)   → primary-tinted via the `success` token family —
 *                     LogViewer routes green to `info` family via the
 *                     debug bucket? No: green logs are *positive*, so we
 *                     reuse the existing semantic `success` (we don't
 *                     ship a separate `success` tone in TONE_CLASSES, so
 *                     we collapse to `info` — green is rare and `info`
 *                     reads as positive on every default preset). For
 *                     callers who need a true success color, that's what
 *                     `level: "info"` with `message: "✓ …"` is for.
 * - 33/43 (yellow)  → warning
 * - 34/44 (blue)    → info
 * - 35/45 (magenta) → debug (categorical, themed via --primary)
 * - 36/46 (cyan)    → info
 * - 37/47 (white)   → undefined (default fg)
 *
 * The `90+` bright variants and `40+` backgrounds collapse onto the same
 * tones — bright/normal differentiation goes through the `bold` flag and
 * Tailwind weight, not a fresh color scale.
 */
const COLOR_TONE: Record<number, LogTone | undefined> = {
  30: 'muted',
  31: 'destructive',
  32: 'info', // see note above
  33: 'warning',
  34: 'info',
  35: 'debug',
  36: 'info',
  37: undefined,
  90: 'muted',
  91: 'destructive',
  92: 'info',
  93: 'warning',
  94: 'info',
  95: 'debug',
  96: 'info',
  97: undefined,
};

// Background colors carry no semantic weight in our log surface — we
// strip them entirely. Recognise them for parser-correctness only.
const BG_CODES = new Set([40, 41, 42, 43, 44, 45, 46, 47, 100, 101, 102, 103, 104, 105, 106, 107]);

interface State {
  tone?: LogTone;
  bold?: boolean;
  dim?: boolean;
  italic?: boolean;
  underline?: boolean;
}

function applyCode(state: State, code: number): void {
  if (code === 0) {
    state.tone = undefined;
    state.bold = false;
    state.dim = false;
    state.italic = false;
    state.underline = false;
    return;
  }
  if (code === 1) {
    state.bold = true;
    return;
  }
  if (code === 2) {
    state.dim = true;
    return;
  }
  if (code === 3) {
    state.italic = true;
    return;
  }
  if (code === 4) {
    state.underline = true;
    return;
  }
  if (code === 22) {
    state.bold = false;
    state.dim = false;
    return;
  }
  if (code === 23) {
    state.italic = false;
    return;
  }
  if (code === 24) {
    state.underline = false;
    return;
  }
  if (code === 39) {
    state.tone = undefined;
    return;
  }
  if (BG_CODES.has(code) || code === 49) {
    // background — ignore
    return;
  }
  if (code in COLOR_TONE) {
    state.tone = COLOR_TONE[code];
  }
}

// Matches a single SGR escape: `\x1b[…m`. The CSI parameter bytes are
// digits separated by `;`. The terminator `m` distinguishes SGR from
// cursor / mode escapes — those are dropped silently.
//
// eslint-disable-next-line no-control-regex
const ANSI_REGEX = /\x1b\[((?:\d+;?)*)m/g;

/**
 * Parse an ANSI-tinted string into styled segments. The returned array is
 * cheap to memoize per log entry — segments are short and immutable.
 */
export function parseAnsi(input: string): AnsiSegment[] {
  if (!input) return [];
  // Fast path — no escape byte at all.
  if (input.indexOf('\x1b') === -1) {
    return [{ text: input }];
  }

  const segments: AnsiSegment[] = [];
  const state: State = {};
  let cursor = 0;

  // Reset the global regex's lastIndex (it persists across calls).
  ANSI_REGEX.lastIndex = 0;

  let match: RegExpExecArray | null;
  while ((match = ANSI_REGEX.exec(input)) !== null) {
    const slice = input.slice(cursor, match.index);
    if (slice) {
      segments.push({ text: slice, ...state });
    }

    const params = match[1] ?? '';
    if (params === '') {
      // `\x1b[m` ≡ `\x1b[0m`
      applyCode(state, 0);
    } else {
      const codes = params.split(';').map((p) => Number.parseInt(p, 10) || 0);
      // 256-color / truecolor: step over their tail so the rest of the
      // sequence doesn't get misread.
      for (let i = 0; i < codes.length; i += 1) {
        const code = codes[i];
        if (code === undefined) continue;
        if ((code === 38 || code === 48) && codes[i + 1] === 5) {
          // 256-color — skip the index byte
          i += 2;
          continue;
        }
        if ((code === 38 || code === 48) && codes[i + 1] === 2) {
          // truecolor — skip 3 RGB bytes
          i += 4;
          continue;
        }
        applyCode(state, code);
      }
    }

    cursor = match.index + match[0].length;
  }

  const tail = input.slice(cursor);
  if (tail) {
    segments.push({ text: tail, ...state });
  }

  // If the entire string was escape sequences, return at least one empty
  // segment so the renderer has something to key off of.
  return segments.length > 0 ? segments : [{ text: '' }];
}

/**
 * Strip ANSI sequences for plain-text use (copy-to-clipboard, search,
 * download). Keeps every printable character.
 */
export function stripAnsi(input: string): string {
  if (!input || input.indexOf('\x1b') === -1) return input;
  return input.replace(ANSI_REGEX, '');
}

/**
 * Resolve a segment's Tailwind classes against the LogViewer tone table.
 * Bold / dim / italic / underline come from Tailwind utilities and stack
 * orthogonally on the tone color.
 */
export function classesForSegment(segment: AnsiSegment): string {
  const parts: string[] = [];
  if (segment.tone) {
    parts.push(TONE_CLASSES[segment.tone].text);
  }
  if (segment.bold) parts.push('font-semibold');
  if (segment.dim) parts.push('opacity-70');
  if (segment.italic) parts.push('italic');
  if (segment.underline) parts.push('underline');
  return parts.join(' ');
}

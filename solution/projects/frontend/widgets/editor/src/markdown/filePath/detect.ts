/**
 * File-path detection + display helpers for the chat editor's "file chip"
 * decoration. Pure, side-effect-free, and unit-testable — no TipTap /
 * ProseMirror / React imports live here so the same functions back the
 * standalone `<FilePathChip>` and the editor decoration alike.
 *
 * Design goal: **LOW false-positive**. We only treat a token as a local
 * file path when it matches an explicit, unambiguous ABSOLUTE shape —
 * never a bare relative token (`./x`, `src/y`) and never a web URL. See
 * `reports/research.md` for the rationale (there is no single universal
 * path regex; detect by safe shapes only).
 */

// ── Match result ──

export interface FilePathMatch {
  /** Inclusive start offset into the scanned string. */
  start: number;
  /** Exclusive end offset into the scanned string. */
  end: number;
  /** The matched path text (already trailing-punctuation-trimmed). */
  path: string;
}

// ── Detector ──

/**
 * Trailing sentence punctuation that, when it hangs off the END of a
 * detected path token, is almost certainly prose and not part of the
 * filename — trim it. Real filenames effectively never end in these.
 * (A leading `.` like a dotfile is fine — we only trim the tail.)
 */
const TRAILING_PUNCT = new Set([
  '.', ',', ')', ']', '}', ';', ':', '!', '?',
  '«', '»', '"', "'", '”', '’', '…',
]);

/**
 * The four absolute path shapes, as a single alternation. Each alternative
 * is whitespace-bounded by construction (`\S` runs, no raw spaces). Order
 * matters: more specific schemes (`file://`, UNC, drive) come before the
 * bare Unix root so the longest correct form wins.
 *
 * - `file://…`            — `file:` URI (any non-space tail).
 * - `\\server\share…`     — Windows UNC (two leading backslashes).
 * - `C:\…` / `C:/…`       — Windows drive (single letter + `:` + slash).
 * - `~/…`                 — home-relative (Unix/macOS).
 * - `/seg/seg…`           — Unix/macOS absolute, REQUIRES ≥2 segments so a
 *                           lone `/` or prose `a / b` never matches.
 *
 * Unicode is allowed inside segments (`@projects`, Cyrillic dirs) — we
 * match on "not whitespace" rather than an ASCII allow-list, then strip
 * trailing punctuation afterwards.
 */
const PATH_RE = new RegExp(
  [
    // file:// URI — scheme then a non-space tail.
    String.raw`file:\/\/\S+`,
    // UNC: \\server\share...  (need a host char after the two slashes).
    String.raw`\\\\[^\s\\/][^\s]*`,
    // Windows drive: C:\... or C:/... (single drive letter).
    String.raw`[A-Za-z]:[\\/][^\s]*`,
    // Home: ~/...
    String.raw`~[\\/][^\s]+`,
    // Unix/macOS absolute: /seg/seg... — at least TWO segments. A
    // segment is a run of non-space, non-separator chars; we require
    // a separator + segment to repeat at least once after the root.
    String.raw`\/[^\s\\/]+(?:[\\/][^\s\\/]+)+[\\/]?`,
  ].join('|'),
  'gu',
);

/**
 * Trim trailing prose punctuation from a raw token. Repeats so multiple
 * trailing marks (`manifest.md).` → `manifest.md`) all come off, but
 * stops as soon as the tail is a normal path char. We never trim into an
 * empty string.
 */
function trimTrailingPunct(raw: string): string {
  let end = raw.length;
  while (end > 1 && TRAILING_PUNCT.has(raw[end - 1]!)) {
    end -= 1;
  }
  return raw.slice(0, end);
}

/**
 * Find every absolute local file path in `text`.
 *
 * Returns matches in document order with `{ start, end, path }` where
 * `[start, end)` are offsets into the ORIGINAL string (after trailing-
 * punctuation trimming, `end` points just past the kept path — the
 * trimmed punctuation is left out of the range so the chip doesn't cover
 * it). Web URLs (`https://x.com/y`), bare relative tokens, and a lone
 * prose slash are intentionally NOT matched.
 */
export function findFilePaths(text: string): FilePathMatch[] {
  if (!text) return [];

  const out: FilePathMatch[] = [];
  PATH_RE.lastIndex = 0;
  let m: RegExpExecArray | null;

  while ((m = PATH_RE.exec(text)) !== null) {
    const raw = m[0];
    const start = m.index;

    // Guard against a zero-width match (shouldn't happen with these
    // alternatives, but keep the loop safe).
    if (raw.length === 0) {
      PATH_RE.lastIndex += 1;
      continue;
    }

    // Leading-boundary guard. A real path token starts the string or
    // follows whitespace / an opening delimiter. If it's glued onto a
    // preceding non-space char it's a SUBSTRING of a larger token — most
    // importantly a web URL's path (`https://x.com/y/z` → the `/y/z`
    // would otherwise match the Unix-absolute shape). Reject those.
    if (start > 0) {
      const prev = text[start - 1]!;
      if (!/[\s([{<«"'‘“]/.test(prev)) continue;
    }

    const trimmed = trimTrailingPunct(raw);
    // A bare drive root (`C:\`) or `~/` with nothing meaningful is not a
    // useful chip — but the regexes above already require a tail segment,
    // so `trimmed` here is always a real path. Still, skip if trimming
    // collapsed it to a non-path remnant.
    if (trimmed.length < 2) continue;

    out.push({
      start,
      end: start + trimmed.length,
      path: trimmed,
    });
  }

  return out;
}

// ── Split (separator-agnostic) ──

export interface SplitPath {
  /** Everything before the basename (no trailing separator). */
  dir: string;
  /** Last non-empty path segment (the file or folder name). */
  base: string;
  /**
   * Heuristic: the path points at a directory rather than a file —
   * either it ends in a separator, or its basename has no file
   * extension (a dotted `manifest.md` reads as a file; `positioning`
   * reads as a dir).
   */
  isDir: boolean;
}

/**
 * Strip a `file://` (or `file:`) scheme prefix for display/splitting.
 * `file:///Users/x` → `/Users/x`; `file://host/share` → `host/share`.
 */
function stripFileScheme(path: string): string {
  const lower = path.toLowerCase();
  if (lower.startsWith('file://')) {
    // file:///abs  → /abs   (three slashes: empty host, keep the root)
    // file://host  → host
    return path.slice('file://'.length);
  }
  if (lower.startsWith('file:')) return path.slice('file:'.length);
  return path;
}

/** True when `base` looks like it carries a real file extension. */
function hasExtension(base: string): boolean {
  const dot = base.lastIndexOf('.');
  // No dot, leading dot only (dotfile like `.gitignore` — treat as file),
  // or a trailing dot → decide:
  //  - `.gitignore` (dot at 0) IS a file → has "extension".
  //  - `name.` (dot last) → not a real extension.
  if (dot === -1) return false;
  if (dot === base.length - 1) return false; // trailing dot
  if (dot === 0) return true; // dotfile
  return true;
}

/**
 * Split a path into `{ dir, base, isDir }`, separator-agnostic (handles
 * `/` and `\` mixed). The basename is the last NON-EMPTY segment so a
 * trailing separator (`/Users/me/docs/`) still yields `base = "docs"`
 * and `isDir = true`.
 */
export function splitPath(path: string): SplitPath {
  const cleaned = stripFileScheme(path);
  const endsWithSep = /[\\/]$/.test(cleaned);

  // Split on either separator, drop empty segments (collapses `//`,
  // leading root, trailing sep).
  const segments = cleaned.split(/[\\/]+/).filter((s) => s.length > 0);
  const base = segments.length > 0 ? segments[segments.length - 1]! : cleaned;
  const dirSegments = segments.slice(0, -1);
  const dir = dirSegments.join('/');

  const isDir = endsWithSep || !hasExtension(base);

  return { dir, base, isDir };
}

// ── Truncate (Apple/Finder middle-ellipsis) ──

export interface TruncateOptions {
  /**
   * Approximate max characters for the label. The basename is ALWAYS
   * kept in full (never cut); only the middle collapses. Default 40.
   */
  maxChars?: number;
}

const ELLIPSIS = '…';

/**
 * Produce a compact, Finder/Chrome-style label for a path: the basename
 * is sacred (always shown in full), the MIDDLE collapses to `…`, and a
 * leading root hint is kept when there's room.
 *
 * Examples (maxChars ≈ 40):
 *   /Users/me/dev/proj/positioning/manifest.md
 *     → /Users/…/positioning/manifest.md
 *   /a/b.md                → /a/b.md   (already short — unchanged)
 *   C:\Users\me\notes.md   → C:\…\notes.md (separator preserved? — we
 *                            normalise display to `/` for compactness)
 */
export function truncatePathLabel(path: string, opts: TruncateOptions = {}): string {
  const maxChars = opts.maxChars ?? 40;
  const display = stripFileScheme(path);

  // Short enough — show as-is.
  if (display.length <= maxChars) return display;

  const endsWithSep = /[\\/]$/.test(display);
  const segments = display.split(/[\\/]+/).filter((s) => s.length > 0);
  if (segments.length <= 1) {
    // Single segment longer than maxChars — keep the basename intact
    // (CSS ellipsis is the safety net in the chip).
    return display;
  }

  const base = segments[segments.length - 1]!;
  const baseLabel = endsWithSep ? `${base}/` : base;

  // Detect a leading root hint we can preserve:
  //  - Unix/macOS absolute → leading "/" + first segment.
  //  - Windows drive → "C:".
  //  - `~` home → "~".
  let rootHint = '';
  if (/^[A-Za-z]:[\\/]/.test(display)) {
    rootHint = display.slice(0, 2); // "C:"
  } else if (display.startsWith('~')) {
    rootHint = '~';
  } else if (/^[\\/]/.test(display)) {
    rootHint = `/${segments[0]!}`;
  }

  // The penultimate segment (parent folder) is a useful hint to keep
  // when room allows — `.../positioning/manifest.md`.
  const parent = segments.length >= 2 ? segments[segments.length - 2]! : '';

  // Build candidates from most-informative to least, pick the first that
  // fits within maxChars (the basename is never sacrificed).
  const candidates: string[] = [];
  if (rootHint && parent) {
    candidates.push(`${rootHint}/${ELLIPSIS}/${parent}/${baseLabel}`);
  }
  if (parent) {
    candidates.push(`${ELLIPSIS}/${parent}/${baseLabel}`);
  }
  if (rootHint) {
    candidates.push(`${rootHint}/${ELLIPSIS}/${baseLabel}`);
  }
  candidates.push(`${ELLIPSIS}/${baseLabel}`);

  for (const c of candidates) {
    if (c.length <= maxChars) return c;
  }

  // Even `…/base` overflows (a very long basename) — return it anyway;
  // the chip's CSS `text-overflow: ellipsis` clips the tail visually
  // while the full path stays in the tooltip.
  return `${ELLIPSIS}/${baseLabel}`;
}

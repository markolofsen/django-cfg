/**
 * URL detection + display helpers for the chat editor's "URL chip" node.
 * Pure, side-effect-free, and unit-testable — no TipTap / ProseMirror /
 * React imports live here so the same functions back the editor node and
 * any standalone use alike.
 *
 * Design goal mirrors `../filePath/detect.ts`: **LOW false-positive**. We
 * only treat a token as a URL when it carries an explicit web scheme
 * (`http`/`https`/`ftp`/`mailto`/`file`) or a bare `www.` host — exactly
 * the set the editor's `shouldAutoLinkUrl` whitelist already accepts, so
 * the chip never disagrees with the autolinker. Bare file paths and dotted
 * filenames (`manifest.md`) are intentionally NOT matched here — those are
 * the file-path node's job.
 */

// ── Match result ──

export interface UrlMatch {
  /** Inclusive start offset into the scanned string. */
  start: number;
  /** Exclusive end offset into the scanned string. */
  end: number;
  /**
   * The matched URL text, normalised to a navigable href (a bare `www.`
   * host gets an `https://` prefix so the chip's anchor works). Trailing
   * prose punctuation is trimmed.
   */
  href: string;
  /** The raw matched text exactly as it appeared (no scheme added). */
  raw: string;
}

/**
 * Trailing sentence punctuation that, when it hangs off the END of a
 * detected URL token, is almost certainly prose and not part of the URL —
 * trim it. (A URL effectively never ends in these for display purposes;
 * a real trailing `)` that balances an opening `(` is the classic edge
 * case but rare in a chat composer and not worth the complexity.)
 */
const TRAILING_PUNCT = new Set([
  '.', ',', ')', ']', '}', ';', ':', '!', '?',
  '«', '»', '"', "'", '”', '’', '…',
]);

/**
 * URL shapes, as a single alternation. Each alternative is whitespace-
 * bounded by construction (`\S` runs). Order: explicit schemes first, then
 * the bare `www.` host.
 *
 * - `mailto:user@host`     — mail scheme (no `//`).
 * - `scheme://host/...`    — http/https/ftp/file with authority.
 * - `www.host...`          — schemeless web host (we prepend https).
 */
const URL_RE = new RegExp(
  [
    String.raw`mailto:[^\s]+`,
    String.raw`(?:https?|ftp|file):\/\/[^\s]+`,
    String.raw`www\.[^\s/$.?#][^\s]*`,
  ].join('|'),
  'giu',
);

function trimTrailingPunct(raw: string): string {
  let end = raw.length;
  while (end > 1 && TRAILING_PUNCT.has(raw[end - 1]!)) {
    end -= 1;
  }
  return raw.slice(0, end);
}

/** Normalise a raw token to a navigable href (prepend https for `www.`). */
export function normalizeHref(raw: string): string {
  if (/^www\./i.test(raw)) return `https://${raw}`;
  return raw;
}

/**
 * Find every URL in `text`. Returns matches in document order with
 * `{ start, end, href, raw }` where `[start, end)` are offsets into the
 * ORIGINAL string (after trailing-punctuation trimming). File paths and
 * bare relative tokens are intentionally NOT matched.
 */
export function findUrls(text: string): UrlMatch[] {
  if (!text) return [];

  const out: UrlMatch[] = [];
  URL_RE.lastIndex = 0;
  let m: RegExpExecArray | null;

  while ((m = URL_RE.exec(text)) !== null) {
    const raw = m[0];
    const start = m.index;

    if (raw.length === 0) {
      URL_RE.lastIndex += 1;
      continue;
    }

    // Leading-boundary guard: a real URL token starts the string or
    // follows whitespace / an opening delimiter. Glued onto a preceding
    // non-space char it's a substring of a larger token — reject.
    if (start > 0) {
      const prev = text[start - 1]!;
      if (!/[\s([{<«"'‘“]/.test(prev)) continue;
    }

    const trimmed = trimTrailingPunct(raw);
    if (trimmed.length < 4) continue;

    out.push({
      start,
      end: start + trimmed.length,
      href: normalizeHref(trimmed),
      raw: trimmed,
    });
  }

  return out;
}

// ── Split / label (Chrome-style domain + middle-ellipsis path) ──

export interface SplitUrl {
  /** Host without a leading `www.` (e.g. `github.com`). Empty if unparseable. */
  domain: string;
  /** Host for favicon lookup (with `www.` stripped). */
  host: string;
  /** Path + query + hash, leading `/` included (empty for a bare host). */
  rest: string;
  /** `mailto:` address (no scheme) when the URL is a mail link, else ''. */
  mail: string;
}

/**
 * Split an href into `{ domain, host, rest, mail }`. Uses the platform
 * `URL` parser; falls back to a light regex when `URL` throws (it
 * shouldn't for our matched shapes, but stay robust).
 */
export function splitUrl(href: string): SplitUrl {
  if (/^mailto:/i.test(href)) {
    const mail = href.slice('mailto:'.length);
    const at = mail.lastIndexOf('@');
    const domain = at >= 0 ? mail.slice(at + 1) : '';
    return { domain, host: domain, rest: '', mail };
  }

  try {
    const u = new URL(normalizeHref(href));
    const host = u.hostname.replace(/^www\./i, '');
    const rest = `${u.pathname === '/' ? '' : u.pathname}${u.search}${u.hash}`;
    return { domain: host, host: u.hostname, rest, mail: '' };
  } catch {
    // Best-effort fallback for an unparseable token.
    const noScheme = normalizeHref(href).replace(/^[a-z]+:\/\//i, '');
    const slash = noScheme.indexOf('/');
    const host = (slash >= 0 ? noScheme.slice(0, slash) : noScheme).replace(/^www\./i, '');
    const rest = slash >= 0 ? noScheme.slice(slash) : '';
    return { domain: host, host, rest, mail: '' };
  }
}

const ELLIPSIS = '…';

export interface UrlLabelOptions {
  /**
   * Approximate max characters for the WHOLE label (domain + path). The
   * domain is always kept in full; only the path's middle collapses.
   * Default 40.
   */
  maxChars?: number;
}

/**
 * Produce a compact, Chrome-omnibox-style label for a URL: the domain is
 * sacred (always shown in full), then the path's MIDDLE collapses to `…`
 * while the LAST path segment (often the meaningful slug / filename) is
 * kept.
 *
 * Examples (maxChars ≈ 40):
 *   https://github.com/wailsapp/wails/blob/main/v3/README.md
 *     → github.com/…/README.md
 *   https://github.com/wailsapp/wails
 *     → github.com/wailsapp/wails   (short — unchanged)
 *   mailto:me@example.com → me@example.com
 */
export function truncateUrlLabel(href: string, opts: UrlLabelOptions = {}): string {
  const maxChars = opts.maxChars ?? 40;
  const { domain, rest, mail } = splitUrl(href);

  if (mail) {
    return mail.length <= maxChars ? mail : `${ELLIPSIS}${mail.slice(mail.length - (maxChars - 1))}`;
  }

  const full = `${domain}${rest}`;
  if (full.length <= maxChars) return full;

  // Collapse the path's middle, keeping the last segment.
  const segments = rest.split('/').filter((s) => s.length > 0);
  if (segments.length === 0) {
    // Only a domain, but it's longer than maxChars — return as-is (CSS
    // ellipsis is the safety net in the chip).
    return domain;
  }
  const last = segments[segments.length - 1]!;

  const candidates: string[] = [];
  if (segments.length >= 2) {
    candidates.push(`${domain}/${segments[0]!}/${ELLIPSIS}/${last}`);
  }
  candidates.push(`${domain}/${ELLIPSIS}/${last}`);
  candidates.push(`${domain}/${ELLIPSIS}`);

  for (const c of candidates) {
    if (c.length <= maxChars) return c;
  }
  return `${domain}/${ELLIPSIS}/${last}`;
}

/**
 * Favicon URL for a host via Google's S2 service. Degrades to the globe
 * icon on error (the chip wires an `onerror` handler). Returns '' when the
 * host is empty.
 */
export function faviconUrl(host: string, size = 32): string {
  if (!host) return '';
  return `https://www.google.com/s2/favicons?domain=${encodeURIComponent(host)}&sz=${size}`;
}

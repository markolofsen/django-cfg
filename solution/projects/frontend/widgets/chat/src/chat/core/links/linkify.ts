/**
 * Web links inside plain text: where they are, which are safe to open, and how
 * to show a long one short.
 *
 * Pure functions of a string, like `prose.ts`: no React, no DOM. The renderers
 * (`LinkifiedText` for a person's line, `ChatAnchor` for markdown) only draw
 * what these decide, so the decision is testable without rendering.
 *
 * ## Safe means three schemes
 *
 * `http`, `https` and `mailto`. Anything else (`javascript:`, `data:`, `file:`,
 * an app scheme) is text. A URL with userinfo (`https://google.com@evil.test`)
 * is refused too: it reads as one host and opens another.
 */

import { linkChipLabel } from "./prose";

/** A link found in a text: `[start, end)` indexes into it. */
export interface FoundLink {
  readonly start: number;
  readonly end: number;
  /** What to open: `www.` hosts get `https://`. */
  readonly href: string;
}

/** A range of the text that belongs to something else (an `@` mention). */
export interface TextRange {
  readonly start: number;
  readonly end: number;
}

const SAFE_SCHEME = /^(https?|mailto):/i;

/**
 * The href to open, or `undefined` when it must not be a link.
 *
 * Returns the typed text (with `https://` added to a bare `www.` host), never a
 * normalised copy: what the reader sees on hover is what they wrote.
 */
export function safeHref(raw: string | undefined): string | undefined {
  if (raw === undefined) return undefined;
  const trimmed = raw.trim();
  const candidate = /^www\./i.test(trimmed) ? `https://${trimmed}` : trimmed;
  if (!SAFE_SCHEME.test(candidate)) return undefined;
  // Whitespace, angle brackets and control characters never belong in a href.
  // eslint-disable-next-line no-control-regex -- the control range is the point of this check
  if (/[\s<>"\u0000-\u001f\u007f]/.test(candidate)) return undefined;
  if (/^mailto:/i.test(candidate)) return candidate.length > "mailto:".length ? candidate : undefined;
  try {
    const url = new URL(candidate);
    if (url.hostname === "" || url.username !== "" || url.password !== "") return undefined;
    if (!url.hostname.includes(".") && url.hostname !== "localhost") return undefined;
    return candidate;
  } catch {
    return undefined;
  }
}

// A scheme or `www.` at a word start, then everything up to whitespace.
const CANDIDATE = /(?<![\p{L}\p{N}_])(?:https?:\/\/|mailto:|www\.)[^\s<>"`]+/giu;

const CLOSERS: Readonly<Record<string, string>> = { ")": "(", "]": "[", "}": "{" };

/**
 * Cut the sentence off the end of a match: `see https://x.test/a.` is the
 * address without the full stop; a closing bracket stays only if the url opened
 * one (`https://en.wikipedia.org/wiki/Foo_(bar)`).
 */
function trimTail(match: string): string {
  let end = match.length;
  while (end > 0) {
    const ch = match.charAt(end - 1);
    if (".,;:!?'*_~".includes(ch)) {
      end -= 1;
      continue;
    }
    const opener = CLOSERS[ch];
    if (opener !== undefined) {
      const body = match.slice(0, end);
      const opens = body.split(opener).length - 1;
      const closes = body.split(ch).length - 1;
      if (closes > opens) {
        end -= 1;
        continue;
      }
    }
    break;
  }
  return match.slice(0, end);
}

/**
 * Every safe web link in `text`, in order.
 *
 * `skip` are ranges that belong to something else, in practice the `@` mentions
 * `mentionSpans` found. A link overlapping one is not a link, so a mention is
 * never split or turned into an anchor. (A mention needs whitespace before it,
 * so `https://medium.com/@user` is one link and never overlaps a mention.)
 */
export function findLinks(text: string, skip: readonly TextRange[] = []): readonly FoundLink[] {
  const found: FoundLink[] = [];
  for (const match of text.matchAll(CANDIDATE)) {
    const raw = trimTail(match[0]);
    const href = safeHref(raw);
    if (href === undefined) continue;
    const start = match.index;
    const end = start + raw.length;
    if (skip.some((range) => start < range.end && end > range.start)) continue;
    found.push({ start, end, href });
  }
  return found;
}

/** Elide mark, shared with `prose.ts`. */
const ELLIPSIS = "…";

/**
 * The short form of a link for a bubble: host, the start and end of the path,
 * the query dropped. A dropped query is marked, so the label never claims to be
 * the whole address; the whole address is the title, the copy and the target.
 */
export function linkLabel(href: string, maxChars = 40): string {
  const withoutQuery = href.replace(/\?[^#]*/, "");
  const label = linkChipLabel(withoutQuery, maxChars);
  return withoutQuery !== href && !label.endsWith(ELLIPSIS) ? `${label}${ELLIPSIS}` : label;
}

/** Whether opening the href should use a new tab: web pages do, a mail client does not. */
export function opensInNewTab(href: string): boolean {
  return /^https?:/i.test(href);
}

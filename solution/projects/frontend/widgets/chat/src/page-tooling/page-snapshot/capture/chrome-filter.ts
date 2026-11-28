/**
 * Layout-chrome exclusion.
 *
 * Identifies global navigation / header / footer / sidebar — the
 * "chrome" that surrounds real content. Runs inside every scope tier
 * and again during the walk, so the snapshot never wastes tokens on
 * app shell the user is not asking about.
 *
 * Combines three signals: ARIA landmark roles, the
 * Readability `unlikelyCandidates` class/id regex, and geometry
 * (fixed-position bars).
 */

import { tagName } from './dom-utils';

/** Landmark roles / tags that are chrome by definition. */
const CHROME_ROLES: ReadonlySet<string> = new Set([
  'navigation',
  'banner',
  'contentinfo',
  'complementary',
]);

const CHROME_TAGS: ReadonlySet<string> = new Set([
  'nav',
  'header',
  'footer',
  'aside',
]);

/**
 * Readability's `unlikelyCandidates` regex — class/id tokens that mark
 * an element as non-content. Trimmed to the app-UI-relevant subset.
 */
const UNLIKELY_RE =
  /(^|[\s_-])(nav|navbar|sidebar|side-?bar|menu|header|footer|banner|breadcrumb|toolbar|topbar|appbar|masthead|drawer|skip-?link)([\s_-]|$)/i;

/** Roles that explicitly mark content — never treat these as chrome. */
const CONTENT_RE = /(^|[\s_-])(main|content|article|workspace)([\s_-]|$)/i;

/** Does the element's role / tag make it a landmark-level chrome region. */
function isLandmarkChrome(el: Element): boolean {
  const role = el.getAttribute('role')?.toLowerCase();
  if (role && CHROME_ROLES.has(role)) return true;
  if (CHROME_TAGS.has(tagName(el))) return true;
  return false;
}

/** Does the class/id name pattern mark the element as chrome. */
function isNamedChrome(el: Element): boolean {
  const tokens = `${el.className ?? ''} ${el.id ?? ''}`;
  if (!tokens.trim()) return false;
  if (CONTENT_RE.test(tokens)) return false;
  return UNLIKELY_RE.test(tokens);
}

/** Is the element a fixed/sticky global bar (geometry signal). */
function isFixedBar(el: Element): boolean {
  if (!(el instanceof HTMLElement)) return false;
  const pos = getComputedStyle(el).position;
  if (pos !== 'fixed' && pos !== 'sticky') return false;
  // A fixed bar is typically thin relative to the viewport.
  const rect = el.getBoundingClientRect();
  const thin =
    rect.height < window.innerHeight * 0.25 ||
    rect.width < window.innerWidth * 0.25;
  return thin;
}

/**
 * Is this element layout chrome that should be excluded from capture.
 *
 * A content landmark (`<main>`, `[role=main]`, or a content-named
 * element) is never chrome, even if nested oddly.
 */
export function isChrome(el: Element): boolean {
  const role = el.getAttribute('role')?.toLowerCase();
  if (role === 'main' || tagName(el) === 'main') return false;

  return isLandmarkChrome(el) || isNamedChrome(el) || isFixedBar(el);
}

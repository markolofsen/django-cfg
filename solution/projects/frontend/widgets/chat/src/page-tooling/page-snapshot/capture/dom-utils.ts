/**
 * Shared DOM helpers for capture — visibility, geometry, classification.
 *
 * All layout reads (`getBoundingClientRect`, `getComputedStyle`) live
 * here so callers can keep them out of the recursive walk — interleaving
 * layout reads with the walk would cause layout thrashing.
 */

/** Tags that never contribute to a snapshot. */
export const SKIP_TAGS: ReadonlySet<string> = new Set([
  'script',
  'style',
  'noscript',
  'meta',
  'link',
  'head',
  'template',
  'br',
  'hr',
]);

/** Tags excluded but replaced with a placeholder (may carry text). */
export const PLACEHOLDER_TAGS: ReadonlySet<string> = new Set([
  'canvas',
  'svg',
  'iframe',
]);

/**
 * Tags whose zero geometry must not mark them invisible — leaf controls
 * and media that legitimately have no text content, plus table
 * structure with no own box. Visibility for these is style-only.
 */
const ZERO_BOX_OK: ReadonlySet<string> = new Set([
  // Form controls — leaf, often no text content.
  'input',
  'select',
  'textarea',
  'button',
  'option',
  'optgroup',
  // Media / embedded — captured as placeholders.
  'canvas',
  'svg',
  'img',
  'iframe',
  // Table structure with no own box.
  'tr',
  'tbody',
  'thead',
  'tfoot',
  'colgroup',
  'col',
]);

/**
 * Is an element rendered — not display:none / visibility:hidden /
 * collapsed to nothing.
 *
 * Visibility is decided primarily from computed *style* (reliable
 * everywhere, including jsdom which does no layout). Geometry is only a
 * secondary signal: a real zero-size box marks an element hidden, but
 * an environment that reports zero geometry for everything (jsdom) must
 * not blank the whole tree — so a zero box is only disqualifying when
 * the element also has no text and no children.
 */
export function isVisible(el: Element): boolean {
  if (!(el instanceof HTMLElement)) return false;
  const style = getComputedStyle(el);
  if (style.display === 'none') return false;
  if (style.visibility === 'hidden' || style.visibility === 'collapse') {
    return false;
  }
  if (style.opacity === '0') return false;
  if (el.hasAttribute('hidden')) return false;
  if (el.getAttribute('aria-hidden') === 'true') return false;

  if (ZERO_BOX_OK.has(tagName(el))) return true;

  const rect = el.getBoundingClientRect();
  if (rect.width === 0 && rect.height === 0) {
    // A truly empty zero-box is hidden; but an element with content and
    // a zero box is likely just an un-laid-out environment — keep it.
    const hasContent =
      el.children.length > 0 || (el.textContent ?? '').trim().length > 0;
    return hasContent;
  }
  return true;
}

/** Rendered area of an element in CSS pixels. */
export function elementArea(el: Element): number {
  const rect = el.getBoundingClientRect();
  return Math.max(0, rect.width) * Math.max(0, rect.height);
}

/** Ratio of link-text length to total text length in a subtree (0–1). */
export function linkDensity(el: Element): number {
  const total = (el.textContent ?? '').trim().length;
  if (total === 0) return 0;
  let linkChars = 0;
  el.querySelectorAll('a').forEach((a) => {
    linkChars += (a.textContent ?? '').trim().length;
  });
  return Math.min(1, linkChars / total);
}

/** lowercased tag name. */
export function tagName(el: Element): string {
  return el.tagName.toLowerCase();
}

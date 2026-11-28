/**
 * Accessible-name resolution.
 *
 * A pragmatic subset of the ARIA accessible-name algorithm — enough to
 * give the AI a meaningful label for interactive elements. Adapted from
 * cmdop_browser/perception/axtree.py.
 */

import { tagName } from './dom-utils';

/** Trim and collapse whitespace; cap length. */
function clean(text: string, max = 120): string {
  const t = text.replace(/\s+/g, ' ').trim();
  return t.length > max ? `${t.slice(0, max)}…` : t;
}

/** Escape a string for use in a CSS selector (CSS.escape fallback). */
function escapeId(id: string): string {
  if (typeof CSS !== 'undefined' && typeof CSS.escape === 'function') {
    return CSS.escape(id);
  }
  // Minimal fallback: escape characters not valid in an unescaped ident.
  return id.replace(/[^a-zA-Z0-9_-]/g, (ch) => `\\${ch}`);
}

/** Resolve the accessible name of an element. */
export function accessibleName(el: Element): string {
  // aria-label wins.
  const ariaLabel = el.getAttribute('aria-label');
  if (ariaLabel) return clean(ariaLabel);

  // aria-labelledby → referenced element text.
  const labelledBy = el.getAttribute('aria-labelledby');
  if (labelledBy) {
    const parts = labelledBy
      .split(/\s+/)
      .map((id) => document.getElementById(id)?.textContent ?? '')
      .filter(Boolean);
    if (parts.length) return clean(parts.join(' '));
  }

  const tag = tagName(el);

  // Form controls — associated <label>.
  if (tag === 'input' || tag === 'select' || tag === 'textarea') {
    const id = el.getAttribute('id');
    if (id) {
      const label = document.querySelector(`label[for="${escapeId(id)}"]`);
      if (label?.textContent) return clean(label.textContent);
    }
    const wrapping = el.closest('label');
    if (wrapping?.textContent) return clean(wrapping.textContent);
    const placeholder = el.getAttribute('placeholder');
    if (placeholder) return clean(placeholder);
    const name = el.getAttribute('name');
    if (name) return clean(name);
  }

  // Image — alt text.
  if (tag === 'img') {
    const alt = el.getAttribute('alt');
    if (alt) return clean(alt);
  }

  // title attribute fallback.
  const title = el.getAttribute('title');
  if (title) return clean(title);

  // Otherwise the element's own visible text (links, buttons).
  if (el.textContent) return clean(el.textContent);

  return '';
}

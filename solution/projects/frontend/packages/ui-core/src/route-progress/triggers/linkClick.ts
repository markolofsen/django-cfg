/**
 * Which link clicks are page navigations the bar should react to. Pure: it reads the event,
 * the anchor and the base URL, and answers with the destination or `null`.
 */

/** The parts of an anchor we read; a real `HTMLAnchorElement` fits. */
export interface AnchorLike {
  href: string;
  target: string;
  hasAttribute(name: string): boolean;
}

export interface ClickLike {
  button: number;
  metaKey: boolean;
  ctrlKey: boolean;
  shiftKey: boolean;
  altKey: boolean;
  target: { closest?(selector: string): AnchorLike | null } | EventTarget | null;
}

/** Opt-out on one anchor: `<a data-no-route-progress>`. */
export const NO_PROGRESS_ATTR = 'data-no-route-progress';

/** The URL a plain left click on a same-origin link goes to, else `null`. */
export function clickDestination(event: ClickLike, baseHref: string): URL | null {
  if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return null;
  const el = event.target as { closest?(selector: string): AnchorLike | null } | null;
  const anchor = el && typeof el.closest === 'function' ? el.closest('a[href]') : null;
  if (!anchor || typeof anchor.href !== 'string') return null;
  if (anchor.target && anchor.target !== '_self') return null;
  if (anchor.hasAttribute('download') || anchor.hasAttribute(NO_PROGRESS_ATTR)) return null;
  let url: URL;
  try {
    url = new URL(anchor.href, baseHref);
  } catch {
    return null;
  }
  if (url.protocol !== 'http:' && url.protocol !== 'https:') return null;
  if (url.origin !== new URL(baseHref).origin) return null;
  return url;
}

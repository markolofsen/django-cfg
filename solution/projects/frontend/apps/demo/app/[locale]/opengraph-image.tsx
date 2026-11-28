import { brandCard, contentType, size } from '@core/og';

/**
 * The site-wide brand card — the homepage, and the fallback for every route
 * that does not own a card of its own. Next wires it into `og:image` and
 * `twitter:image` by filename; nothing in the layout metadata refers to it.
 *
 * Lives under `[locale]` on purpose: `proxy.ts` sends every dotless path
 * through next-intl, which redirects `/opengraph-image` to
 * `/en/opengraph-image` — a root-level route would 404 there.
 */
export const runtime = 'nodejs';
export const alt = 'djangocfg demo — a minimal Next.js shell for django-cfg';
export { size, contentType };

export default async function OpengraphImage() {
  return brandCard('Next.js shell for django-cfg');
}

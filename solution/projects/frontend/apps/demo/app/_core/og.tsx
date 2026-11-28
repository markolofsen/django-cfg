import { createOgCards, domainFromEnv } from '@djangocfg/widget-ogimage';

import { settings } from './settings';

/**
 * The demo's Open Graph identity, bound once. Every `opengraph-image.tsx`
 * imports `size`/`contentType` from here and calls a fabric — see
 * `widgets/ogimage/README.md` for the rules (nodejs runtime, never throw, no
 * `openGraph.images` above a card).
 */

/** The django-cfg mark: a bracketed "cfg" drawn as inline SVG — satori cannot load icon components. */
function CfgMark() {
  return (
    <svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
      <path d="M8 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h2" />
      <path d="M16 4h2a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-2" />
      <path d="M9 12h6" />
    </svg>
  );
}

export const { size, contentType, brandCard, contentCard } = createOgCards({
  name: settings.app.name,
  description: settings.app.description,
  tagline: 'Type-safe Django, from config to frontend',
  domain: domainFromEnv({ fallback: settings.app.siteUrl }),
  siteUrl: settings.app.siteUrl,
  accentColor: '#61B8FF',
  mark: <CfgMark />,
});

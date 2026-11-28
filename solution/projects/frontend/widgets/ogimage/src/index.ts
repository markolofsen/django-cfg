// ── Recommended API ──────────────────────────────────────────────────────────
// Bind once per app (`app/_lib/og.ts`), then every `opengraph-image.tsx`
// re-exports `size`/`contentType` and calls `brandCard` or `contentCard`.
export { createOgCards, fitDescription, ogFooter, ogImageUrl } from './card';
export type { ContentCardOptions, OgCards, OgCardsConfig } from './card';

// ── Site origin + the metadata trap ──────────────────────────────────────────
export { domainFromEnv, metadataBaseFromEnv, resolvePublicUrl, siteUrlFromEnv, trimTrailingSlash, withoutOgImages } from './url';
export type { SiteUrlOptions } from './url';

// ── Low-level: draw a card directly ──────────────────────────────────────────
export { DEFAULT_OG_THEME, OG_CONTENT_TYPE, OG_SIZE, renderOgImage, titleSizeFor } from './render';
export type { OgImageOptions, OgTheme } from './render';
export { loadOgFonts, OG_FONT_FAMILY } from './fonts';
export type { OgFonts } from './fonts';
export { loadImageDataUri } from './file';

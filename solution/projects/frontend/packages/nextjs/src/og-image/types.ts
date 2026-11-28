/**
 * Per-page OG image intent — the single axis that decides what the OG image is.
 *
 *   'static'              brand image from site config (the default)
 *   { image, alt? }       an exact image URL (e.g. a content screenshot)
 *
 * There is deliberately no "render this title onto a card" case. That was
 * served by a Django endpoint (`/cfg/og/<base64>/`), archived 2026-09-03 —
 * Next.js renders such cards itself via an `opengraph-image` route.
 *
 * That route is not a drop-in, though: both spec cases set `openGraph.images`,
 * and Next.js skips the file convention whenever metadata already does. A page
 * wanting a rendered card must omit the key from its metadata (see
 * `resolveOgImage`), not merely add the route file.
 */
export type OgSpec = 'static' | { image: string; alt?: string }

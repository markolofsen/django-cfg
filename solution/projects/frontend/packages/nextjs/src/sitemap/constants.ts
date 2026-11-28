/**
 * Shared sitemap constants.
 *
 * Pulled out so both the chunk factory (`createDjangoSitemap`) and the
 * index Route Handler (`createSitemapIndex`) agree on the id of the
 * frontend-only static-routes chunk.
 */

export const STATIC_ID = 'static';
export const DEFAULT_INDEX_REVALIDATE = 600;
export const DEFAULT_FEED_REVALIDATE = 3600;

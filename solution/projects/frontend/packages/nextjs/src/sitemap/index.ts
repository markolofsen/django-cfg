/**
 * @djangocfg/nextjs/sitemap
 *
 * Sitemap-index + per-chunk Next.js sitemap factory backed by
 * `django_cfg.modules.django_sitemap`. Handles catalogs up to Google's
 * per-file URL caps without materialising data in the frontend.
 *
 * See `createDjangoSitemap` for the main entry point and `createRobots`
 * for the matching robots.txt factory.
 */

export { createDjangoSitemap } from './sitemap';
export { createSitemapIndex } from './index-route';
export { createRobots } from './robots';
export { encodeChunkId, decodeChunkId } from './ids';
export { selectSources, sourceFilter, tenantSources } from './select';
export { fetchSitemapIndex, fetchSitemapFeed } from './fetch';

export type {
  SitemapChunkInfo,
  SitemapEntry,
  SitemapFeedPage,
  SitemapIndex,
  SitemapSourceInfo,
  CreateDjangoSitemapOptions,
  CreateSitemapIndexOptions,
  CreateRobotsOptions,
  SourceSelector,
  StaticRoute,
} from './types';

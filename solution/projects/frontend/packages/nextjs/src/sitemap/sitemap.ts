/**
 * createDjangoSitemap — factory for Next.js `app/sitemap.ts`.
 *
 * Backed by `django_cfg.modules.django_sitemap`: the backend exposes a
 * paginated JSON feed, this factory turns each chunk into a Next.js
 * sitemap file via `generateSitemaps()`.
 *
 * Usage:
 *
 * ```ts
 * // apps/<app>/app/sitemap.ts
 * import { createDjangoSitemap } from '@djangocfg/nextjs/sitemap';
 *
 * const { generateSitemaps, sitemap } = createDjangoSitemap({
 *   host: process.env.NEXT_PUBLIC_SITE_URL!,
 *   apiUrl: process.env.NEXT_PUBLIC_API_URL!,
 *   staticRoutes: [
 *     { path: '/', changeFrequency: 'daily', priority: 1.0 },
 *     { path: '/catalog', changeFrequency: 'daily', priority: 0.9 },
 *   ],
 * });
 *
 * export { generateSitemaps, sitemap as default };
 * export const revalidate = 3600;
 * ```
 *
 * Without `apiUrl`, the sitemap emits only the static routes — handy for
 * marketing sites that don't have a backend-driven URL space.
 */

import type { MetadataRoute } from 'next';

import {
  DEFAULT_FEED_REVALIDATE,
  DEFAULT_INDEX_REVALIDATE,
  STATIC_ID,
} from './constants';
import { fetchSitemapFeed, fetchSitemapIndex } from './fetch';
import { decodeChunkId, encodeChunkId } from './ids';
import { selectedChunkIds, sourceFilter } from './select';

import type { CreateDjangoSitemapOptions, StaticRoute } from './types';

interface SitemapApi {
  generateSitemaps: () => Promise<Array<{ id: string }>>;
  sitemap: (props: { id: Promise<string> }) => Promise<MetadataRoute.Sitemap>;
}

export function createDjangoSitemap(opts: CreateDjangoSitemapOptions): SitemapApi {
  const {
    host,
    apiUrl,
    staticRoutes = [],
    sources,
    indexRevalidate = DEFAULT_INDEX_REVALIDATE,
    feedRevalidate = DEFAULT_FEED_REVALIDATE,
  } = opts;

  return {
    async generateSitemaps() {
      const ids: Array<{ id: string }> = [{ id: STATIC_ID }];
      if (!apiUrl) return ids;
      const index = await fetchSitemapIndex(apiUrl, indexRevalidate);
      for (const id of selectedChunkIds(index, sources, encodeChunkId)) {
        ids.push({ id });
      }
      return ids;
    },

    async sitemap({ id: idPromise }) {
      const id = await idPromise;

      if (id === STATIC_ID) {
        return renderStatic(host, staticRoutes);
      }

      if (!apiUrl) return [];

      const { source, cursor } = decodeChunkId(id);
      // A chunk this app does not claim renders empty rather than fetching.
      // `generateSitemaps` never mints such an id, but the route stays
      // reachable by hand, and serving another tenant's URLs from a guessed
      // address would undo the filter above.
      if (!sourceFilter(sources)(source)) return [];

      const feed = await fetchSitemapFeed(apiUrl, source, cursor, feedRevalidate);
      return feed.entries.map((e) => ({
        url: `${host}${e.loc}`,
        lastModified: e.lastmod ? new Date(e.lastmod) : undefined,
      }));
    },
  };
}

function renderStatic(host: string, routes: StaticRoute[]): MetadataRoute.Sitemap {
  return routes.map((r) => ({
    url: `${host}${r.path}`,
    changeFrequency: r.changeFrequency,
    priority: r.priority,
  }));
}

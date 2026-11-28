/**
 * createSitemapIndex — Route Handler factory for the sitemap-index XML.
 *
 * Next.js's `generateSitemaps()` API ships chunks at `/sitemap/<id>.xml`
 * but does NOT emit a single sitemap-index document. Without one,
 * robots.txt + crawlers point at a 404 and never discover the chunks.
 * This factory closes that gap: it returns a `GET` Route Handler that
 * mints a `<sitemapindex>` XML listing every chunk the matching
 * `createDjangoSitemap` would produce.
 *
 * Mount it at **`app/sitemap_index.xml/route.ts`** — NOT `sitemap.xml`.
 * `app/sitemap.ts` (where `createDjangoSitemap` lives) already owns
 * `/sitemap.xml` in Next.js's metadata routing, even when its output is
 * fan-out via `generateSitemaps()` and the singular URL serves 404.
 * Putting a route handler at `app/sitemap.xml/route.ts` throws at build
 * time: *Conflicting route and metadata at /sitemap.xml*.
 *
 * Usage — the full pattern with the matching chunk + robots factories:
 *
 * ```ts
 * // apps/<app>/app/sitemap.ts — chunks
 * import { createDjangoSitemap } from '@djangocfg/nextjs/sitemap';
 * const { generateSitemaps, sitemap } = createDjangoSitemap({ ... });
 * export { generateSitemaps, sitemap as default };
 *
 * // apps/<app>/app/sitemap_index.xml/route.ts — the index
 * import { createSitemapIndex } from '@djangocfg/nextjs/sitemap';
 * export const { GET } = createSitemapIndex({
 *   host: process.env.NEXT_PUBLIC_SITE_URL!,
 *   apiUrl: process.env.NEXT_PUBLIC_API_URL!,
 * });
 * export const revalidate = 600;
 *
 * // apps/<app>/app/robots.ts — point crawlers at the index URL above
 * import { createRobots } from '@djangocfg/nextjs/sitemap';
 * const host = process.env.NEXT_PUBLIC_SITE_URL!;
 * export default createRobots({
 *   host,
 *   sitemap: `${host}/sitemap_index.xml`,
 * });
 * ```
 *
 * Keep `host` / `apiUrl` in sync with the same app's `app/sitemap.ts`
 * — the index just enumerates the chunks the other file emits.
 */

import {
  DEFAULT_INDEX_REVALIDATE,
  STATIC_ID,
} from './constants';
import { fetchSitemapIndex } from './fetch';
import { encodeChunkId } from './ids';
import { selectedChunks } from './select';

import type { CreateSitemapIndexOptions } from './types';

interface SitemapIndexRoute {
  GET: () => Promise<Response>;
}

export function createSitemapIndex(opts: CreateSitemapIndexOptions): SitemapIndexRoute {
  const {
    host,
    apiUrl,
    sources,
    indexRevalidate = DEFAULT_INDEX_REVALIDATE,
    includeStatic = true,
  } = opts;

  return {
    async GET() {
      // A shard's lastmod is the newest row it holds. Never the request time: that says every shard changed on every
      // read, and a crawler learns to ignore it. No known date → no <lastmod> (the static shard has none).
      const chunks: { id: string; lastmod: string | null }[] = includeStatic
        ? [{ id: STATIC_ID, lastmod: null }]
        : [];

      if (apiUrl) {
        const index = await fetchSitemapIndex(apiUrl, indexRevalidate);
        chunks.push(...selectedChunks(index, sources, encodeChunkId));
      }

      const body = renderIndex(host, chunks);

      return new Response(body, {
        status: 200,
        headers: {
          'content-type': 'application/xml; charset=utf-8',
          // Mirror the per-chunk revalidate so a cached CDN edge expires
          // at the same cadence as the index it points at.
          'cache-control': `public, s-maxage=${indexRevalidate}, stale-while-revalidate=${indexRevalidate}`,
        },
      });
    },
  };
}

function renderIndex(host: string, chunks: { id: string; lastmod: string | null }[]): string {
  const lines: string[] = [];
  lines.push('<?xml version="1.0" encoding="UTF-8"?>');
  lines.push('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">');
  for (const { id, lastmod } of chunks) {
    lines.push('  <sitemap>');
    lines.push(`    <loc>${escapeXml(`${host}/sitemap/${id}.xml`)}</loc>`);
    if (lastmod) lines.push(`    <lastmod>${escapeXml(lastmod)}</lastmod>`);
    lines.push('  </sitemap>');
  }
  lines.push('</sitemapindex>');
  return lines.join('\n');
}

function escapeXml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

/**
 * createRobots — factory for Next.js `app/robots.ts`.
 *
 * Emits a single `User-Agent: *` block plus a Sitemap pointer. Disallow
 * defaults cover the common cases (auth, account, API surface) — override
 * per app if needed.
 *
 * The `sitemap` default `${host}/sitemap.xml` only makes sense for the
 * single-file case. When the app uses `createDjangoSitemap`
 * (`generateSitemaps()` → chunked output) **plus** `createSitemapIndex`
 * — the canonical pairing — pass an explicit
 * `sitemap: \`${host}/sitemap_index.xml\`` to point crawlers at the
 * index. The default `/sitemap.xml` will serve a 404 in that setup
 * (Next.js reserves it for the metadata route but doesn't emit content
 * there).
 *
 * Usage:
 *
 * ```ts
 * // apps/<app>/app/robots.ts
 * import { createRobots } from '@djangocfg/nextjs/sitemap';
 *
 * const host = process.env.NEXT_PUBLIC_SITE_URL!;
 *
 * export default createRobots({
 *   host,
 *   disallow: ['/account/', '/auth', '/api/', '/apix/'],
 *   sitemap: `${host}/sitemap_index.xml`, // matches createSitemapIndex
 * });
 * ```
 */

import type { MetadataRoute } from 'next';

import type { CreateRobotsOptions } from './types';

const DEFAULT_DISALLOW = ['/account/', '/auth', '/api/'];

export function createRobots(opts: CreateRobotsOptions): () => MetadataRoute.Robots {
  const { host, disallow = DEFAULT_DISALLOW, sitemap } = opts;
  return () => ({
    rules: [{ userAgent: '*', allow: '/', disallow }],
    sitemap: sitemap ?? `${host}/sitemap.xml`,
    host,
  });
}

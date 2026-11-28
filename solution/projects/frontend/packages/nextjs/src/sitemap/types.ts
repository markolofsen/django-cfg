/**
 * Sitemap module — types
 *
 * Wire-contract for `django_cfg.modules.django_sitemap` JSON endpoints
 * plus the public option types for `createDjangoSitemap` and
 * `createRobots`.
 */

import type { ChangeFreq } from '../types';

// ── Wire contract with Django backend ───────────────────────────────────

export interface SitemapChunkInfo {
  id: string;
  cursor_to: string | null;
  count_estimate: number;
  /** Newest `lastmod_field` value among the chunk's rows (ISO), or null. Older backends omit it. */
  lastmod?: string | null;
}

export interface SitemapSourceInfo {
  name: string;
  chunks: SitemapChunkInfo[];
  total_estimate: number;
}

export interface SitemapIndex {
  sources: SitemapSourceInfo[];
  generated_at: string;
  ttl_seconds: number;
}

export interface SitemapEntry {
  loc: string;
  lastmod?: string | null;
}

export interface SitemapFeedPage {
  source: string;
  chunk_id: string;
  count: number;
  has_more: boolean;
  next_cursor: string | null;
  entries: SitemapEntry[];
}

// ── Public option types ─────────────────────────────────────────────────

/**
 * Which backend sources a frontend claims: a list of names, or a predicate.
 *
 * Omit for every source in the index — right whenever the backend serves
 * this frontend alone. Pass one when several frontends share a backend, so
 * each emits only the URLs its own host can resolve. See `tenantSources`
 * for the `<source>-<tenant>` convention.
 */
export type SourceSelector = string[] | ((name: string) => boolean);

export interface StaticRoute {
  path: string;
  changeFrequency?: ChangeFreq;
  priority?: number;
}

export interface CreateDjangoSitemapOptions {
  /** Canonical site host, e.g. `https://vamcar.com`. URLs in the sitemap
   *  are joined as `${host}${loc}`. */
  host: string;

  /** Django backend base URL. When omitted, backend chunks are skipped
   *  and only `staticRoutes` are emitted (single-chunk sitemap). */
  apiUrl?: string;

  /** Frontend-only routes the backend doesn't know about. Auth/account
   *  pages should NOT be listed here. */
  staticRoutes?: StaticRoute[];

  /** Backend sources to emit. Default: every source the index reports.
   *  Keep in step with the same app's `createSitemapIndex`. */
  sources?: SourceSelector;

  /** Index revalidate window in seconds. Default: 600. */
  indexRevalidate?: number;

  /** Feed (chunk) revalidate window in seconds. Default: 3600. */
  feedRevalidate?: number;
}

export interface CreateSitemapIndexOptions {
  /** Canonical site host, e.g. `https://vamcar.com`. Chunk URLs in the
   *  index are emitted as `${host}/sitemap/<id>.xml`. */
  host: string;

  /** Django backend base URL. When omitted, the index lists only the
   *  static chunk (mirrors `createDjangoSitemap` without `apiUrl`). */
  apiUrl?: string;

  /** Revalidate window in seconds for both the upstream `index/` fetch
   *  and the emitted XML's `s-maxage`. Default: 600. */
  indexRevalidate?: number;

  /** Backend sources to list. Default: every source the index reports.
   *  MUST match the same app's `createDjangoSitemap` — a mismatch
   *  advertises chunks the sitemap route will not build. */
  sources?: SourceSelector;

  /** Include the `static` chunk id at the top of the index. Turn off if
   *  the app's `sitemap.ts` opts out of `staticRoutes`. Default: true. */
  includeStatic?: boolean;
}

export interface CreateRobotsOptions {
  host: string;
  /** Disallow patterns. Default: ['/account/', '/auth', '/api/']. */
  disallow?: string[];
  /** Override sitemap URL. Default: `${host}/sitemap.xml`.
   *  When using `createDjangoSitemap` + `createSitemapIndex`, pass
   *  `${host}/sitemap_index.xml` — see `createSitemapIndex` JSDoc. */
  sitemap?: string;
}

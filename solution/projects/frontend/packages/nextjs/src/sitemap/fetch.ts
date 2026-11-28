/**
 * Sitemap fetch helpers.
 *
 * During `next build` a failure becomes an empty payload, so a Django outage
 * does not fail the build. At runtime it throws: ISR then keeps serving the
 * last good copy. An empty payload there would be cached for the whole
 * revalidate window — a sitemap index with only the static chunk, which
 * crawlers and IndexNow diffs read as every listing removed.
 */

import type { SitemapFeedPage, SitemapIndex } from './types';

/**
 * Next.js refuses to write a fetch response larger than 2MB into its data
 * cache. It logs one line and serves the response uncached, so `revalidate`
 * silently becomes a no-op and every regeneration refetches the full payload
 * from Django. Nothing else surfaces this, so we measure the body ourselves.
 */
const NEXT_DATA_CACHE_LIMIT = 2 * 1024 * 1024;

// One warning per URL: `sitemap()` runs once per chunk per build, and a
// repeated line for the same feed reads as a new problem rather than the
// same one.
const oversizeWarned = new Set<string>();

/**
 * Read the body as text so its exact size is known, then parse.
 *
 * `Content-Length` is not a substitute: it is absent under chunked transfer
 * and reports the compressed size when the response is gzipped, while the
 * 2MB ceiling applies to the decoded bytes Next.js would store.
 */
async function parseAndCheckSize<T>(r: Response, url: string, label: string): Promise<T> {
  const text = await r.text();
  const bytes = new TextEncoder().encode(text).length;
  if (bytes > NEXT_DATA_CACHE_LIMIT && !oversizeWarned.has(url)) {
    oversizeWarned.add(url);
    console.warn(
      `[sitemap] ${label} is ${bytes} bytes, over Next.js's 2MB data-cache ceiling: ` +
        `revalidate is inert for this feed and every regeneration refetches it from Django. ` +
        `Lower the backend page_size if the extra load matters — note 50,000 URLs is the ` +
        `sitemap protocol's own maximum, so a large payload here is not itself a bug.`,
    );
  }
  return JSON.parse(text) as T;
}

/** True while `next build` prerenders; false in the serving process. */
const isBuilding = (): boolean => process.env.NEXT_PHASE === 'phase-production-build';

function degrade<T>(fallback: T, reason: string, err?: unknown): T {
  if (!isBuilding()) {
    throw new Error(`[sitemap] ${reason}; keeping the last good copy`, { cause: err });
  }
  console.warn(`[sitemap] ${reason}; falling back to empty during build`, err ?? '');
  return fallback;
}

const EMPTY_INDEX: SitemapIndex = {
  sources: [],
  generated_at: new Date(0).toISOString(),
  ttl_seconds: 60,
};

const emptyFeed = (source: string, cursor: string | null): SitemapFeedPage => ({
  source,
  chunk_id: `${source}-empty`,
  count: 0,
  has_more: false,
  next_cursor: cursor,
  entries: [],
});

export async function fetchSitemapIndex(
  apiUrl: string,
  revalidate: number,
): Promise<SitemapIndex> {
  const url = `${apiUrl}/cfg/sitemap/index/`;
  try {
    const r = await fetch(url, {
      next: { revalidate },
    });
    if (!r.ok) return degrade(EMPTY_INDEX, `index fetch returned ${r.status}`);
    return await parseAndCheckSize<SitemapIndex>(r, url, 'index');
  } catch (err) {
    return degrade(EMPTY_INDEX, 'index fetch failed', err);
  }
}

export async function fetchSitemapFeed(
  apiUrl: string,
  source: string,
  cursor: string | null,
  revalidate: number,
): Promise<SitemapFeedPage> {
  const params = new URLSearchParams({ source });
  if (cursor) params.set('cursor', cursor);
  const url = `${apiUrl}/cfg/sitemap/feed/?${params}`;
  try {
    const r = await fetch(url, {
      next: { revalidate },
    });
    if (!r.ok) return degrade(emptyFeed(source, cursor), `feed ${source} returned ${r.status}`);
    return await parseAndCheckSize<SitemapFeedPage>(r, url, `feed ${source}`);
  } catch (err) {
    return degrade(emptyFeed(source, cursor), `feed ${source} fetch failed`, err);
  }
}

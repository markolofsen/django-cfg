/**
 * Which backend sources a frontend claims.
 *
 * `GET /cfg/sitemap/index/` answers for the whole Django project — every
 * source any installed app registered. One frontend is not always entitled
 * to all of them: a backend serving several brands registers a source per
 * brand (`properties-caribbean`, `properties-bali`), and each brand's app
 * must emit only its own, or it advertises the other's URLs under its own
 * host — every one of them a 404, and the sitemap that carries them is
 * discredited whole.
 *
 * The selector lives here, shared, for the same reason `STATIC_ID` does:
 * `createDjangoSitemap` enumerates the chunks and `createSitemapIndex`
 * enumerates them again for the index document. If the two applied
 * different filters, the index would advertise shards the chunk route
 * refuses to build — and that mismatch is invisible until a crawler reads
 * both. One function, called by both, cannot drift.
 *
 * Source NAMES are the contract. The module ships no notion of a brand or
 * a tenant, and it should not: the backend chose what its source names
 * mean, and only the app knows which of them are its own.
 */

import type { SitemapIndex, SitemapSourceInfo, SourceSelector } from './types';

/**
 * A predicate from whatever the caller passed.
 *
 * Omitted means every source — the single-tenant default, and what every
 * caller before this option existed already relied on.
 */
export function sourceFilter(select: SourceSelector | undefined): (name: string) => boolean {
  if (select === undefined) return () => true;
  if (typeof select === 'function') return select;
  const allowed = new Set(select);
  return (name) => allowed.has(name);
}

/** The index's sources, narrowed to those the caller claims. */
export function selectSources(
  index: SitemapIndex,
  select: SourceSelector | undefined,
): SitemapSourceInfo[] {
  const keep = sourceFilter(select);
  return index.sources.filter((source) => keep(source.name));
}

/**
 * Every chunk id the selected sources produce, in index order.
 *
 * The one place `(source, chunk)` becomes an id, so the chunk route and the
 * index document enumerate the same set by construction.
 */
export function selectedChunkIds(
  index: SitemapIndex,
  select: SourceSelector | undefined,
  encode: (source: string, cursor: string | null) => string,
): string[] {
  const ids: string[] = [];
  for (const source of selectSources(index, select)) {
    for (const chunk of source.chunks) {
      ids.push(encode(source.name, chunk.cursor_to));
    }
  }
  return ids;
}

/**
 * Like `selectedChunkIds`, with each chunk's own lastmod (the newest row it holds), for the index document.
 */
export function selectedChunks(
  index: SitemapIndex,
  select: SourceSelector | undefined,
  encode: (source: string, cursor: string | null) => string,
): { id: string; lastmod: string | null }[] {
  const out: { id: string; lastmod: string | null }[] = [];
  for (const source of selectSources(index, select)) {
    for (const chunk of source.chunks) {
      out.push({ id: encode(source.name, chunk.cursor_to), lastmod: chunk.lastmod ?? null });
    }
  }
  return out;
}

/**
 * A selector for one tenant of a multi-brand backend.
 *
 * Matches the `<source>-<tenant>` names that a backend registering per
 * tenant emits. It splits on the LAST hyphen and compares the tail exactly,
 * rather than testing a suffix: `endsWith('-bali')` is correct for
 * `properties-bali` but the same shape reads `pricing-plans-premium` as
 * belonging to a `premium` tenant, and a substring match is not a contract.
 *
 * ```ts
 * sources: tenantSources('bali')   // properties-bali, communities-bali, …
 * ```
 *
 * Sources with no hyphen never match: an untenanted source belongs to the
 * project rather than to a brand, and claiming it for one is the error this
 * function exists to prevent.
 */
export function tenantSources(tenant: string): (name: string) => boolean {
  return (name) => {
    const sep = name.lastIndexOf('-');
    return sep !== -1 && name.slice(sep + 1) === tenant;
  };
}

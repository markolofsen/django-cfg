/**
 * Sitemap chunk id encoding.
 *
 * Each Next.js sitemap file is addressed by an opaque string id. We
 * round-trip a `(source, cursor)` pair through that id so the default
 * sitemap handler knows which Django chunk to fetch.
 *
 * Separator `--` is unambiguous: backend cursors use URL-safe base64 (`-_`).
 */

export function encodeChunkId(source: string, cursor: string | null): string {
  return `${source}--${cursor ?? ''}`;
}

export function decodeChunkId(id: string): { source: string; cursor: string | null } {
  const sep = id.indexOf('--');
  if (sep === -1) return { source: id, cursor: null };
  const source = id.slice(0, sep);
  const cursorRaw = id.slice(sep + 2);
  return { source, cursor: cursorRaw === '' ? null : cursorRaw };
}

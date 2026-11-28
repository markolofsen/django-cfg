import type { ApiEndpoint } from '../../types';

/** DOM-safe anchor for a single endpoint.
 *
 *  Two forms:
 *  - Scoped (``schemaId`` provided) — ``ep-<schema>-<method>-<slug>``.
 *    Used in ``sections`` mode where endpoints from different schemas
 *    coexist on one page and would otherwise collide.
 *  - Flat — ``ep-<method>-<slug>``. Used in ``selector`` mode where
 *    only one schema is mounted at a time. */
export function endpointAnchor(
  ep: Pick<ApiEndpoint, 'method' | 'path'>,
  schemaId?: string | null,
): string {
  const slug = ep.path
    .replace(/^https?:\/\/[^/]+/, '')
    .replace(/[{}]/g, '')
    .replace(/[^a-zA-Z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .toLowerCase();
  const schemaSlug = schemaId ? `${slugifySchemaId(schemaId)}-` : '';
  return `ep-${schemaSlug}${ep.method.toLowerCase()}-${slug}`;
}

/** Canonical slug for a schema id — safe for anchors and hash fragments. */
export function slugifySchemaId(id: string): string {
  return id.replace(/[^a-zA-Z0-9_-]+/g, '-').replace(/^-+|-+$/g, '');
}

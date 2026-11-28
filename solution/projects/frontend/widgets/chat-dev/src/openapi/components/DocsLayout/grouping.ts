/**
 * Shared grouping / sort for the docs layout.
 *
 * Sidebar and the docs longread MUST use the same order — otherwise
 * scrollspy highlights jump around as the user scrolls (the sidebar's
 * ordered list doesn't match the visual order of sections in the docs).
 * This module is the single source of truth for that ordering.
 */

import type { ApiEndpoint, SchemaSource } from '../../types';
import { longestCommonPrefix } from './sidebarLabel';

export type EndpointGroup = {
    category: string;
    endpoints: ApiEndpoint[];
    /** Longest ``/``-aligned prefix shared by every endpoint in this
     *  group. Used by the sidebar to strip the redundant group prefix
     *  from fallback labels. */
    commonPrefix: string;
};

/** A schema's worth of categorised endpoints. The outer level of the
 *  ``sections`` sidebar iterates over these. */
export type SchemaSection = {
    source: SchemaSource;
    groups: EndpointGroup[];
};

const METHOD_ORDER: Record<string, number> = {
    GET: 0,
    HEAD: 1,
    POST: 2,
    PUT: 3,
    PATCH: 4,
    DELETE: 5,
    OPTIONS: 6,
    TRACE: 7,
};

const methodRank = (ep: ApiEndpoint) => METHOD_ORDER[ep.method] ?? 99;

/** Ordinal string compare — `<`/`>`, not `localeCompare`, so ordering is
 *  locale-independent and identical on every machine. */
const cmp = (a: string, b: string) => (a < b ? -1 : a > b ? 1 : 0);

/**
 * Stable, deterministic ordering so two different renders with the
 * same endpoint list always produce the same visual sequence.
 *
 * Groups: alphabetical by tag/category, with ``Other`` pinned to the
 * bottom (spec-less endpoints should not steal the top slot).
 *
 * Within a group: endpoints sorted by path first (so related resources
 * cluster), then by HTTP method (read → write → delete).
 */
export function groupEndpoints(list: ApiEndpoint[]): EndpointGroup[] {
    const byCategory = new Map<string, ApiEndpoint[]>();
    for (const ep of list) {
        const key = String(ep.category);
        const bucket = byCategory.get(key);
        if (bucket) bucket.push(ep);
        else byCategory.set(key, [ep]);
    }

    const all: EndpointGroup[] = [...byCategory].map(([category, endpoints]) => ({
        category,
        // Path first so related resources cluster, then method rank.
        // `sort` mutates, so sort a copy — `endpoints` is read again below.
        endpoints: [...endpoints].sort(
            (a, b) => cmp(a.path, b.path) || methodRank(a) - methodRank(b),
        ),
        commonPrefix: longestCommonPrefix(endpoints.map((e) => e.path)),
    }));

    // "Other" sinks to the bottom regardless of alphabet.
    const other = all.filter((g) => g.category === 'Other');
    const named = all.filter((g) => g.category !== 'Other');
    named.sort((a, b) => cmp(a.category.toLowerCase(), b.category.toLowerCase()));
    return [...named, ...other];
}

/** Flatten grouped endpoints back into a linear list that preserves
 *  group order + within-group order. This is the canonical order for
 *  both the sidebar and the docs longread. */
export function flattenGrouped(groups: EndpointGroup[]): ApiEndpoint[] {
    return groups.flatMap((g) => g.endpoints);
}

/** Build per-schema sections in the same order as the original
 *  ``schemas`` array. Schemas with zero endpoints are kept so users see
 *  an empty-state placeholder instead of "the section silently vanished". */
export function buildSchemaSections(
    sources: SchemaSource[],
    endpointsBySchema: Record<string, ApiEndpoint[]>,
): SchemaSection[] {
    return sources.map((source) => ({
        source,
        groups: groupEndpoints(endpointsBySchema[source.id] ?? []),
    }));
}

/** Flatten schema-sections into a linear endpoint list. Used by scrollspy
 *  and by the docs longread to render endpoints in the exact same order
 *  as the sidebar. */
export function flattenSchemaSections(sections: SchemaSection[]): ApiEndpoint[] {
    return sections.flatMap((s) => flattenGrouped(s.groups));
}

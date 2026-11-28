/**
 * URL utilities for the OpenAPI playground.
 *
 * Consolidated here to avoid the pre-existing split where
 * ``substituteUrlParameters`` lived in formatters.ts, base URL priority
 * lived inside ``useOpenApiSchema``, query params were never assembled
 * at all (that was a bug), and ``resolveAbsoluteUrl`` was tacked on
 * later.
 *
 * Conceptual model: a request URL is built from four layers, highest
 * priority first:
 *
 *   1. An absolute override URL the user pasted (rare — not plumbed
 *      through the UI today, but the shape supports it).
 *   2. ``baseUrl`` — from ``SchemaSource.baseUrl`` → ``PlaygroundConfig.baseUrl``
 *      → ``schema.servers[0].url``.
 *   3. Endpoint path template (``/pet/{petId}``) + substituted path params.
 *   4. Query string built from parameters that don't match any path
 *      placeholder.
 *
 * Every helper below lives on one of those layers. ``UrlBuilder`` wires
 * them together when the caller has all four; individual functions are
 * exported for cases that only need one step (e.g. ``relativePath``
 * for display in the sidebar).
 */

import type { ApiEndpoint } from '../types';

// ─── Path substitution ────────────────────────────────────────────────────────

const PATH_PARAM_RE = /\{([^{}]+)\}/g;

/**
 * Return the list of ``{name}`` placeholders in a path template.
 * Preserves order, deduplicates.
 */
export function extractPathPlaceholders(template: string): string[] {
    const seen = new Set<string>();
    const out: string[] = [];
    for (const match of template.matchAll(PATH_PARAM_RE)) {
        const name = match[1]!;
        if (!seen.has(name)) {
            seen.add(name);
            out.push(name);
        }
    }
    return out;
}

/**
 * Replace ``{name}`` placeholders with values from ``values``. Values
 * are URL-path-encoded with ``encodeURIComponent`` — safe for single
 * segments but escapes ``/`` too. That's intentional: a user typing
 * ``a/b`` into a path param should get ``a%2Fb`` so the server receives
 * the intended single segment, not two.
 *
 * Values are only substituted when non-empty after trimming.
 */
export function substitutePath(template: string, values: Record<string, string>): string {
    return template.replace(PATH_PARAM_RE, (whole, name) => {
        const v = values[name];
        return v && v.trim() !== '' ? encodeURIComponent(v) : whole;
    });
}

/** Placeholders that have no non-empty value in ``values``. */
export function unfilledPlaceholders(
    template: string,
    values: Record<string, string>,
): string[] {
    return extractPathPlaceholders(template).filter(
        (name) => !(values[name] ?? '').trim(),
    );
}

// ─── Query assembly ───────────────────────────────────────────────────────────

/**
 * Append a query string to ``url`` from the keys of ``values`` that
 * are not path placeholders in ``pathTemplate``. Existing query strings
 * are preserved: new keys are merged, existing keys are overwritten.
 *
 * Empty values are skipped (a form field that was left blank does not
 * become ``?foo=`` on the wire).
 */
export function appendQuery(
    url: string,
    values: Record<string, string>,
    pathTemplate: string,
): string {
    const pathNames = new Set(extractPathPlaceholders(pathTemplate));
    const queryEntries = Object.entries(values).filter(
        ([name, value]) => !pathNames.has(name) && value && value.trim() !== '',
    );
    if (queryEntries.length === 0) return url;

    // Split any existing query so we can merge cleanly.
    const [base, existingQuery = ''] = url.split('?', 2);
    const params = new URLSearchParams(existingQuery);
    for (const [k, v] of queryEntries) params.set(k, v);
    const qs = params.toString();
    return qs ? `${base}?${qs}` : (base ?? url);
}

// ─── Absolute / relative ──────────────────────────────────────────────────────

/**
 * Prepend ``window.location.origin`` when the URL is relative so the
 * result is runnable from a terminal via curl. No-op on SSR or when
 * already absolute.
 */
export function resolveAbsolute(url: string): string {
    if (!url) return url;
    if (/^https?:\/\//i.test(url)) return url;
    if (typeof window === 'undefined') return url;
    if (url.startsWith('//')) return `${window.location.protocol}${url}`;
    if (url.startsWith('/')) return `${window.location.origin}${url}`;
    return url;
}

/** Pull just the path out of any URL (absolute or relative). The
 *  ``URL`` parser percent-encodes path segments, which turns OpenAPI
 *  template braces (``{id}``) into ``%7Bid%7D``. We restore those so
 *  unfilled templates render as the readable form authors wrote. */
export function relativePath(url: string): string {
    try {
        return new URL(url).pathname.replace(/%7B/gi, '{').replace(/%7D/gi, '}');
    } catch {
        return url;
    }
}

/**
 * Concatenate URL segments with exactly one slash between each. Works
 * whether inputs have trailing/leading slashes or not.
 *
 *   joinUrl('https://api.example.com/', '/v3', 'pet') → 'https://api.example.com/v3/pet'
 */
export function joinUrl(...parts: string[]): string {
    const filtered = parts.filter((p) => p !== undefined && p !== null && p !== '');
    return filtered
        .map((p, i) => {
            const s = String(p);
            if (i === 0) return s.replace(/\/+$/, '');
            // Strip leading slashes; preserve trailing slash on the last segment
            // so Django path conventions (/apix/foo/) round-trip correctly.
            const stripped = s.replace(/^\/+/, '');
            if (i === filtered.length - 1) return stripped;
            return stripped.replace(/\/+$/, '');
        })
        .filter((p) => p !== '')
        .join('/');
}

// ─── Base URL resolution ──────────────────────────────────────────────────────

export interface BaseUrlSources {
    /** Highest priority — per-schema override. */
    schemaSource?: string;
    /** Global config-level override. */
    config?: string;
    /** Fallback from the OpenAPI document itself. */
    fromServers?: string;
}

/**
 * Apply the documented priority chain:
 *   ``schemaSource → config → fromServers → ''``.
 */
export function resolveBaseUrl(sources: BaseUrlSources): string {
    return sources.schemaSource || sources.config || sources.fromServers || '';
}

// ─── UrlBuilder ───────────────────────────────────────────────────────────────

/**
 * End-to-end builder that takes an endpoint + user-entered parameters
 * and produces both the fetch URL and a copy-paste-friendly preview.
 */
export class UrlBuilder {
    constructor(
        private readonly endpoint: ApiEndpoint,
        private readonly parameters: Record<string, string>,
    ) {}

    /** What ``fetch()`` receives: substituted path + query string. Origin
     *  is whatever the endpoint template already had (relative paths
     *  stay relative so the browser resolves them against the page). */
    build(): string {
        const substituted = substitutePath(this.endpoint.path, this.parameters);
        return appendQuery(substituted, this.parameters, this.endpoint.path);
    }

    /** Same as ``build()`` but guaranteed absolute — for curl snippets
     *  and anywhere the URL leaves the browser context. */
    buildAbsolute(): string {
        return resolveAbsolute(this.build());
    }

    /** Names of required path/query params still empty. */
    missingRequired(): string[] {
        if (!this.endpoint.parameters) return [];
        return this.endpoint.parameters
            .filter((p) => p.required && !(this.parameters[p.name] ?? '').trim())
            .map((p) => p.name);
    }

    /** Placeholders in the template with no matching value. Usually a
     *  superset of ``missingRequired`` — catches schemas that forgot
     *  to flag a path param as required. */
    unfilledPlaceholders(): string[] {
        return unfilledPlaceholders(this.endpoint.path, this.parameters);
    }
}

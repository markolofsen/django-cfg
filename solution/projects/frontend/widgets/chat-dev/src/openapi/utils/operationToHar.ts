/**
 * OpenAPI endpoint → HAR request.
 *
 * Our in-house code-sample renderers consume a HAR 1.2-shaped request.
 * This module shapes an ``ApiEndpoint`` + user-provided parameter
 * values into that form — path substitution, query-string assembly,
 * header inference, body formatting.
 *
 * We keep the HAR intermediate (rather than a bespoke type) so the
 * renderers match well-known HAR semantics and stay easy to extend.
 */

import type { ApiEndpoint } from '../types';

/** HAR 1.2 request subset that our renderers consume. We don't ship
 *  the full HAR type surface — just the fields that snippet generators
 *  actually read. */
export interface HarRequest {
    method: string;
    url: string;
    httpVersion: string;
    headers: Array<{ name: string; value: string }>;
    queryString: Array<{ name: string; value: string }>;
    cookies: Array<{ name: string; value: string }>;
    headersSize: number;
    bodySize: number;
    postData?: {
        mimeType: string;
        text: string;
    };
}

export interface BuildHarInput {
    endpoint: ApiEndpoint;
    /** Raw body string — whatever the user typed in the playground or
     *  the pre-sampled example. Passed through verbatim; the caller
     *  decides the content shape. */
    body?: string;
    /** Path-param + query-param values, keyed by name. We look up each
     *  parameter on ``endpoint`` to decide whether it slots into the
     *  path or the query string. */
    parameters?: Record<string, string>;
    /** Extra headers to merge in (e.g. ``X-API-Key``, ``Authorization``).
     *  Later entries with the same name override earlier ones. */
    headers?: Record<string, string>;
    /** Override the request URL's base. When absent we use
     *  ``endpoint.path`` as-is (extractor already prepended base URL). */
    baseUrl?: string;
}

/** Split a template path into path vs query. Substitutes ``{id}``-style
 *  placeholders using the provided parameter map; unused entries flow
 *  into the query string. */
function buildUrl(
    endpoint: ApiEndpoint,
    parameters: Record<string, string>,
    baseUrl?: string,
): { url: string; queryString: HarRequest['queryString'] } {
    const pathParamNames = new Set(
        (endpoint.parameters ?? [])
            .filter((p) => endpoint.path.includes(`{${p.name}}`))
            .map((p) => p.name),
    );

    let path = endpoint.path;
    for (const name of pathParamNames) {
        const value = parameters[name];
        if (value === undefined || value === '') continue;
        path = path.replaceAll(`{${name}}`, encodeURIComponent(value));
    }

    const queryString: HarRequest['queryString'] = [];
    for (const param of endpoint.parameters ?? []) {
        if (pathParamNames.has(param.name)) continue;
        const value = parameters[param.name];
        if (value === undefined || value === '') continue;
        queryString.push({ name: param.name, value });
    }

    const url = baseUrl ? `${baseUrl.replace(/\/+$/, '')}${path.startsWith('/') ? path : `/${path}`}` : path;
    return { url, queryString };
}

/** Build a HAR 1.2 request from an API endpoint + current form values. */
export function buildHarRequest(input: BuildHarInput): HarRequest {
    const { endpoint, body, parameters = {}, headers = {}, baseUrl } = input;
    const { url, queryString } = buildUrl(endpoint, parameters, baseUrl);

    const hasBody = Boolean(body && body.trim().length > 0);
    const bodyMime = hasBody
        ? 'application/json'
        : undefined;

    // Merge headers. Caller wins, but we default Content-Type for bodies
    // and Accept for JSON endpoints — snippet consumers expect these.
    const mergedHeaders: Record<string, string> = {};
    if (hasBody && bodyMime) mergedHeaders['Content-Type'] = bodyMime;
    mergedHeaders['Accept'] = 'application/json';
    for (const [k, v] of Object.entries(headers)) {
        if (v === undefined || v === '') continue;
        mergedHeaders[k] = v;
    }

    const har: HarRequest = {
        method: endpoint.method.toUpperCase(),
        url,
        httpVersion: 'HTTP/1.1',
        headers: Object.entries(mergedHeaders).map(([name, value]) => ({ name, value })),
        queryString,
        cookies: [],
        headersSize: -1,
        bodySize: hasBody ? new TextEncoder().encode(body!).length : 0,
    };

    if (hasBody && bodyMime) {
        har.postData = { mimeType: bodyMime, text: body! };
    }

    return har;
}

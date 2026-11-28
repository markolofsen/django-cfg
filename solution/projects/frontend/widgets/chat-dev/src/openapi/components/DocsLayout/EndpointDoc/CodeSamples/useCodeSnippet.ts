'use client';

import { useMemo } from 'react';

import type { ApiEndpoint } from '../../../../types';
import {
    CODE_SAMPLE_TARGETS,
    renderSnippet,
    type CodeSampleTargetId,
} from '../../../../utils/codeSamples';
import { buildHarRequest } from '../../../../utils/operationToHar';
import { resolveAbsolute } from '../../../../utils/url';

interface UseCodeSnippetInput {
    endpoint: ApiEndpoint;
    body?: string;
    parameters?: Record<string, string>;
    headers?: Record<string, string>;
    baseUrl?: string;
    activeId: CodeSampleTargetId;
}

interface UseCodeSnippetResult {
    /** Fully-rendered snippet string. Always present — falls back to an
     *  "unavailable" message if the generator returns null, so the
     *  consumer can always mount ``PrettyCode``. */
    snippet: string;
    /** Prism language id matching ``activeId`` — passed to PrettyCode so
     *  it picks the right highlighter. */
    prism: string;
}

/** Encapsulates HAR build + snippet render + memoisation for the Code
 *  Samples block. Kept as a hook (rather than inline ``useMemo`` blocks
 *  in the component) so unit tests can exercise the snippet pipeline
 *  independently of React rendering. */
export function useCodeSnippet({
    endpoint,
    body,
    parameters,
    headers,
    baseUrl,
    activeId,
}: UseCodeSnippetInput): UseCodeSnippetResult {
    const effectiveBody = body ?? endpoint.requestBody?.example;

    // Build the HAR once per input change — every tab rebuilds its
    // snippet from this shared request shape.
    //
    // ``endpoint.path`` already carries the schema's ``servers[0].url``
    // (joined upstream in ``useOpenApiSchema``). Usually that's a path
    // like ``/api/v3/pet`` — good enough for same-origin fetch, wrong
    // for curl/python/go which need a runnable absolute URL. We hand
    // off to ``resolveAbsolute`` so the snippet is copy-pasteable from
    // a terminal without the user having to edit the host in manually.
    //
    // Priority: explicit ``baseUrl`` prop > resolved origin > bare path.
    const har = useMemo(() => {
        const h = buildHarRequest({
            endpoint,
            body: effectiveBody,
            parameters,
            headers,
            baseUrl,
        });
        return baseUrl ? h : { ...h, url: resolveAbsolute(h.url) };
    }, [endpoint, effectiveBody, parameters, headers, baseUrl]);

    return useMemo(() => {
        const target = CODE_SAMPLE_TARGETS.find((t) => t.id === activeId)!;
        const code = renderSnippet(har, activeId);
        return {
            snippet: code ?? `// Snippet for ${target.label} is unavailable for this request.`,
            prism: target.prism,
        };
    }, [har, activeId]);
}

'use client';

import { LazyPrettyCode as PrettyCode } from '@djangocfg/widget-kit/pretty-code/lazy';
import type { ApiEndpoint } from '../../../../types';
import { useEndpointDocContext } from '../context';
import { useEndpointDocStore } from '../store';
import { useActiveCodeTab } from '../store/selectors';
import { LanguageTabs } from './LanguageTabs';
import { useCodeSnippet } from './useCodeSnippet';

interface CodeSamplesProps {
    endpoint: ApiEndpoint;
    /** Optional body to include in generated snippets. When omitted we
     *  use ``endpoint.requestBody?.example`` if present, so the snippet
     *  shows a realistic payload out of the box. */
    body?: string;
    /** Parameter values to substitute into the URL. Missing path params
     *  fall back to ``{name}`` placeholders so the snippet still
     *  illustrates the shape. */
    parameters?: Record<string, string>;
    /** Extra headers to include in snippets (e.g. a picked API key). */
    headers?: Record<string, string>;
    /** Base URL override — falls back to ``endpoint.path`` which
     *  already has the resolved base URL prepended by the extractor. */
    baseUrl?: string;
}

/** Code samples block: language tab bar + highlighted snippet. The
 *  outer Section wrapper (collapsible) lives one level up; this
 *  component is always "open" from its own perspective. */
export function CodeSamples({ endpoint, body, parameters, headers, baseUrl }: CodeSamplesProps) {
    const { endpointId } = useEndpointDocContext();
    const activeId = useActiveCodeTab(endpointId);
    const setCodeTab = useEndpointDocStore((s) => s.setCodeTab);

    const { snippet, prism } = useCodeSnippet({
        endpoint,
        body,
        parameters,
        headers,
        baseUrl,
        activeId,
    });

    return (
        <div className="space-y-2.5">
            <LanguageTabs activeId={activeId} onChange={(id) => setCodeTab(endpointId, id)} />
            <PrettyCode
                data={snippet}
                language={prism as never}
                isCompact
                maxLines={20}
            />
        </div>
    );
}

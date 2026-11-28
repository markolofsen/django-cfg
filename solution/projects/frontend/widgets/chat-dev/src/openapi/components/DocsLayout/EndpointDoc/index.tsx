'use client';

import React from 'react';

import type { ApiEndpoint } from '../../../types';
import { endpointAnchor } from '../anchor';
import { CodeSamples } from './CodeSamples';
import { EndpointDocProvider } from './context';
import { EndpointHeader } from './Header';
import { Parameters } from './Parameters';
import { RequestBody } from './RequestBody';
import { Responses } from './Responses';
import { Section } from './Section';
import type { SectionId } from './types';

interface EndpointDocProps {
    endpoint: ApiEndpoint;
    /** Is this endpoint currently loaded in the sticky playground? */
    isLoadedInPlayground: boolean;
    onTryIt: () => void;
    /** Scoping prefix for the anchor, so endpoints from different schemas
     *  don't collide on a single page. Falls back to ``endpoint.schemaId``. */
    schemaId?: string | null;
}

/** Card that documents one API endpoint: header + a stack of collapsible
 *  sections (parameters, request body, responses, code samples). The
 *  component itself is a thin orchestrator — each child folder owns its
 *  own rendering concerns and reads the endpoint identity from context. */
export function EndpointDoc({ endpoint, isLoadedInPlayground, onTryIt, schemaId }: EndpointDocProps) {
    const scopedSchemaId = schemaId ?? endpoint.schemaId ?? null;
    const anchor = endpointAnchor(endpoint, scopedSchemaId);
    const pathParams = endpoint.parameters?.filter((p) => endpoint.path.includes(`{${p.name}}`)) ?? [];
    const queryParams = endpoint.parameters?.filter((p) => !endpoint.path.includes(`{${p.name}}`)) ?? [];

    const hasParameters = pathParams.length > 0 || queryParams.length > 0;
    const hasResponses = (endpoint.responses?.length ?? 0) > 0;

    // Collect section ids that actually render so the header's
    // expand/collapse-all toggle only touches visible sections.
    // ``codeSamples`` is always present — it synthesises a snippet
    // even for parameter-less endpoints.
    const presentSections: SectionId[] = [];
    if (hasParameters) presentSections.push('parameters');
    if (endpoint.requestBody) presentSections.push('requestBody');
    presentSections.push('codeSamples');
    if (hasResponses) presentSections.push('responses');

    return (
        <EndpointDocProvider endpointId={anchor} method={endpoint.method}>
            <section
                id={anchor}
                data-endpoint-anchor={anchor}
                data-schema-id={scopedSchemaId ?? ''}
                className="scroll-mt-24 py-10 first:pt-0"
                // ``content-visibility: auto`` lets the browser skip layout
                // + paint for endpoint cards that are off-screen — a big
                // win for large specs (hundreds of endpoints) with no
                // behavioural change. ``contain-intrinsic-size`` supplies a
                // height estimate so the scrollbar stays stable before a
                // card is first rendered.
                style={{ contentVisibility: 'auto', containIntrinsicSize: 'auto 480px' }}
            >
                <EndpointHeader
                    endpoint={endpoint}
                    anchor={anchor}
                    isLoadedInPlayground={isLoadedInPlayground}
                    onTryIt={onTryIt}
                    presentSections={presentSections}
                />

                <div className="mt-8 space-y-5">
                    {hasParameters && (
                        <Section
                            id="parameters"
                            title="Parameters"
                            badge={pathParams.length + queryParams.length}
                        >
                            <Parameters pathParams={pathParams} queryParams={queryParams} />
                        </Section>
                    )}
                    {endpoint.requestBody && (
                        <Section id="requestBody" title="Request body">
                            <RequestBody body={endpoint.requestBody} />
                        </Section>
                    )}
                    <Section id="codeSamples" title="Code samples">
                        <CodeSamples endpoint={endpoint} />
                    </Section>
                    {hasResponses && (
                        <Section
                            id="responses"
                            title="Responses"
                            badge={endpoint.responses!.length}
                        >
                            <Responses responses={endpoint.responses!} />
                        </Section>
                    )}
                </div>
            </section>
        </EndpointDocProvider>
    );
}

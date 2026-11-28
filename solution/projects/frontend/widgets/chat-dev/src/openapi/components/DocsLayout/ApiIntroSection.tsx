'use client';

import React from 'react';

import { MarkdownMessage } from '@djangocfg/widget-code/markdown-message';
import type { ApiEndpoint, OpenApiInfo, OpenApiSchema } from '../../types';
import { SchemaCopyMenu } from './SchemaCopyMenu';

interface ApiIntroSectionProps {
    info: OpenApiInfo;
    schema: OpenApiSchema | null;
    endpoints: ApiEndpoint[];
    resolvedBaseUrl?: string;
}

interface BaseUrlRow {
    url: string;
    description?: string;
}

export function ApiIntroSection({ info, schema, endpoints, resolvedBaseUrl }: ApiIntroSectionProps) {
    // Prefer the *resolved* base URL whenever we have one — that's the
    // URL actual requests target, not the raw ``servers[0].url`` from
    // the spec (which can be a bare path like ``/api/v3``). Fall back
    // to the spec's ``servers`` list so specs that document multiple
    // servers keep showing all of them.
    const baseUrlRows: BaseUrlRow[] = resolvedBaseUrl
        ? [{ url: resolvedBaseUrl, description: info.servers?.[0]?.description }]
        : (info.servers ?? []).map((s) => ({ url: s.url, description: s.description }));

    return (
        <section className="pb-10 mb-10 border-b">
            <div className="flex items-start justify-between gap-4 flex-wrap">
                <div className="flex items-center gap-3 flex-wrap min-w-0">
                    <h1 className="text-3xl font-semibold tracking-tight text-foreground leading-tight">
                        {info.title}
                    </h1>
                    <span className="inline-flex items-center rounded-full bg-muted px-2 py-0.5 font-mono text-[11px] text-muted-foreground">
                        v{info.version}
                    </span>
                </div>
                <SchemaCopyMenu
                    schema={schema}
                    endpoints={endpoints}
                    baseUrl={resolvedBaseUrl}
                />
            </div>

            {info.description && (
                <div className="mt-4 text-muted-foreground">
                    <MarkdownMessage content={info.description} />
                </div>
            )}

            {baseUrlRows.length > 0 && (
                <div className="mt-6 space-y-2">
                    <h4 className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/60">
                        Base URL
                    </h4>
                    <div className="space-y-1.5">
                        {baseUrlRows.map((row, i) => (
                            <div key={`${row.url}-${i}`} className="flex items-baseline gap-2 flex-wrap">
                                <code className="font-mono text-xs px-2 py-1 rounded bg-muted border">
                                    {row.url}
                                </code>
                                {row.description && (
                                    <span className="text-xs text-muted-foreground">
                                        {row.description}
                                    </span>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </section>
    );
}

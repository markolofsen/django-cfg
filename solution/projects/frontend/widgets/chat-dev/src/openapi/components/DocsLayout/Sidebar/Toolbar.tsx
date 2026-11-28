'use client';

import React from 'react';

import { Combobox } from '@djangocfg/ui-core/components';

import type { ApiEndpoint, OpenApiSchema, SchemaSource } from '../../../types';
import { SchemaCopyMenu } from '../SchemaCopyMenu';
import { SearchInput } from './SearchInput';

interface ToolbarProps {
    schemas: SchemaSource[];
    currentSchemaId: string | null;
    onSchemaChange: (id: string) => void;
    showSchemaSelector: boolean;

    search: string;
    onSearchChange: (v: string) => void;

    /** Active-schema endpoints + raw document — drive the Copy-for-AI
     *  CTA that sits under the search input. ``null``/empty disables it. */
    endpoints: ApiEndpoint[];
    rawSchema?: OpenApiSchema | null;
    resolvedBaseUrl?: string;
}

/** Filter / control panel of the sidebar. Groups the schema selector,
 *  search box, and the Copy-for-AI CTA into a single visually cohesive
 *  block so they read as "one toolbar" rather than separate affordances
 *  stacked on top of each other.
 *
 *  The Copy CTA sits directly under the search input — it's a quiet
 *  secondary action, full-width, and previously hid behind a tiny
 *  icon in the brand row where users couldn't see it. */
export function Toolbar({
    schemas,
    currentSchemaId,
    onSchemaChange,
    showSchemaSelector,
    search,
    onSearchChange,
    endpoints,
    rawSchema,
    resolvedBaseUrl,
}: ToolbarProps) {
    const schemaOptions = React.useMemo(
        () => schemas.map((s) => ({ value: s.id, label: s.name })),
        [schemas],
    );

    const copyReady = rawSchema !== null && rawSchema !== undefined && endpoints.length > 0;
    const schemaSelectorNode = showSchemaSelector ? (
        <Combobox
            options={schemaOptions}
            value={currentSchemaId ?? ''}
            onValueChange={(id) => id && onSchemaChange(id)}
            placeholder="Select API"
            searchPlaceholder="Search APIs…"
            emptyText="No APIs found"
            className="w-full h-8 text-xs"
        />
    ) : null;
    const copyMenuNode = copyReady ? (
        <SchemaCopyMenu
            schema={rawSchema ?? null}
            endpoints={endpoints}
            baseUrl={resolvedBaseUrl}
            variant="footer"
            side="bottom"
        />
    ) : null;

    return (
        <div className="shrink-0 border-b px-3 py-2.5 space-y-2">
            {schemaSelectorNode}
            <SearchInput value={search} onChange={onSearchChange} />
            {copyMenuNode}
        </div>
    );
}

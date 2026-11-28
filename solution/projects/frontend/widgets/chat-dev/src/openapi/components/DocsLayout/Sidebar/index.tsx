'use client';

import React, { useMemo, useState } from 'react';

import type { ApiEndpoint, OpenApiInfo, OpenApiSchema, SchemaSource } from '../../../types';
import { ScrollArea } from '../../shared/ui';
import { BrandHeader } from './BrandHeader';
import { buildFlatVM, buildSectionsVM } from './buildVM';
import { SidebarBody } from './SidebarBody';
import { Toolbar } from './Toolbar';
import type { SidebarBodyVM } from './types';
import { useDebouncedValue } from './useDebouncedValue';

export interface DocsSidebarProps {
    info: OpenApiInfo | null;
    /** Active-schema endpoints — used by ``selector`` mode. */
    endpoints: ApiEndpoint[];
    /** All configured schemas (used by both modes). */
    schemas: SchemaSource[];
    currentSchemaId: string | null;
    onSchemaChange: (id: string) => void;
    activeEndpointId: string | null;
    selectedVersion: string;
    onNavigate: (anchor: string, schemaId?: string | null) => void;
    /** Presentation mode. Default: ``selector`` (back-compat). */
    grouping?: 'selector' | 'sections';
    /** Required for ``sections`` mode — endpoints grouped by their source
     *  schema id. The sidebar renders them as two-level sections. */
    endpointsBySchema?: Record<string, ApiEndpoint[]>;
    /** Raw active schema + resolved base URL — used by the Copy-for-AI
     *  CTA in the toolbar. ``null`` hides the button. */
    rawSchema?: OpenApiSchema | null;
    resolvedBaseUrl?: string;
}

/** Docs sidebar orchestrator. Thin — each child folder owns its own
 *  rendering; this file wires props, debounces search, and decides
 *  which view-model builder to call. */
export function DocsSidebar({
    info,
    endpoints,
    schemas,
    currentSchemaId,
    onSchemaChange,
    activeEndpointId,
    selectedVersion,
    onNavigate,
    grouping = 'selector',
    endpointsBySchema,
    rawSchema,
    resolvedBaseUrl,
}: DocsSidebarProps) {
    const [search, setSearch] = useState('');
    const debouncedSearch = useDebouncedValue(search);

    const body = useMemo<SidebarBodyVM>(() => {
        if (grouping === 'sections') {
            return buildSectionsVM(
                schemas,
                endpointsBySchema ?? {},
                selectedVersion,
                debouncedSearch,
                'ALL',
                activeEndpointId,
            );
        }
        return buildFlatVM(
            endpoints,
            selectedVersion,
            debouncedSearch,
            'ALL',
            activeEndpointId,
        );
    }, [
        grouping,
        schemas,
        endpointsBySchema,
        endpoints,
        selectedVersion,
        debouncedSearch,
        activeEndpointId,
    ]);

    const hasMultipleSchemas = schemas.length > 1;
    const showSchemaSelector = grouping === 'selector' && hasMultipleSchemas;

    return (
        <aside className="flex flex-col h-full min-h-0 border-r bg-muted/10">
            <BrandHeader info={info} />
            <Toolbar
                schemas={schemas}
                currentSchemaId={currentSchemaId}
                onSchemaChange={onSchemaChange}
                showSchemaSelector={showSchemaSelector}
                search={search}
                onSearchChange={setSearch}
                endpoints={endpoints}
                rawSchema={rawSchema}
                resolvedBaseUrl={resolvedBaseUrl}
            />
            <ScrollArea>
                <SidebarBody body={body} onNavigate={onNavigate} />
            </ScrollArea>
        </aside>
    );
}

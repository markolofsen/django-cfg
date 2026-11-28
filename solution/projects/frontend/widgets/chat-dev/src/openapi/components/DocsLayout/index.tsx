'use client';

import React, { useCallback, useMemo, useRef, useState } from 'react';

import { Skeleton } from '@djangocfg/ui-core/components';
import { useMediaQuery } from '@djangocfg/ui-core/hooks';

import useOpenApiSchema from '../../hooks/useOpenApiSchema';
import { useDocsUrlSync, type ParsedHash } from '../../hooks/useDocsUrlSync';
import { usePlaygroundContext } from '../../context/PlaygroundContext';
import type { ApiEndpoint, LoadedSchemaEntry } from '../../types';
import { EndpointDraftSync } from '../shared/EndpointDraftSync';
import { slugifySchemaId } from './anchor';
import { DocsSidebar } from './Sidebar';
import { DocsView, type DocsViewHandle } from './DocsView';
import { SlideInPlayground } from './SlideInPlayground';
import { TryItSheet } from './TryItSheet';

// ─── Root ─────────────────────────────────────────────────────────────────────

export const DocsLayout: React.FC = () => {
    const { state, config, setSelectedEndpoint } = usePlaygroundContext();
    // The docs layout has a sidebar + docs column that already eat ~260px
    // before the slide-in opens. Below 1024px the slide-in (min 720 wide)
    // leaves docs with <250px — unreadable — so we fall back to the
    // mobile-style ``TryItSheet`` on those viewports.
    const isDesktop = useMediaQuery('(min-width: 1024px)');
    const isMobile = !isDesktop;

    const grouping = config.schemaGrouping ?? 'selector';
    const preloadAll = grouping === 'sections';
    const urlSyncEnabled =
        config.urlSync === undefined
            ? true
            : typeof config.urlSync === 'boolean'
                ? config.urlSync
                : Boolean(config.urlSync.enabled);

    const {
        endpoints,
        schemaInfo,
        rawSchema,
        resolvedBaseUrl,
        loading,
        error,
        schemas,
        currentSchema,
        setCurrentSchema,
        schemasData,
    } = useOpenApiSchema({
        schemas: config.schemas,
        defaultSchemaId: config.defaultSchemaId,
        baseUrl: config.baseUrl,
        preloadAll,
    });

    const [activeAnchor, setActiveAnchor] = useState<string | null>(null);
    const [activeSchemaId, setActiveSchemaId] = useState<string | null>(null);
    const [sheetOpen, setSheetOpen] = useState(false);
    const docsRef = useRef<DocsViewHandle | null>(null);

    // Desktop slide-in is driven directly by ``selectedEndpoint``. Keeping a
    // separate open-state would mean two sources of truth for the same
    // semantic — "which endpoint is loaded into the playground".
    const slideOpen = !isMobile && state.selectedEndpoint !== null;

    // Per-schema endpoint map for the sections sidebar. ``keyBy`` makes the
    // lookup O(1) at render time instead of scanning schemasData in each
    // CategoryBlock — a win for 10+ schemas.
    const endpointsBySchema = useMemo<Record<string, ApiEndpoint[]>>(() => {
        if (grouping !== 'sections') return {};
        const byId = new Map(schemasData.map((e: LoadedSchemaEntry) => [e.source.id, e]));
        const out: Record<string, ApiEndpoint[]> = {};
        for (const src of schemas) out[src.id] = byId.get(src.id)?.endpoints ?? [];
        return out;
    }, [grouping, schemasData, schemas]);

    const handleTry = useCallback(
        (ep: ApiEndpoint) => {
            setSelectedEndpoint(ep);
            if (isMobile) setSheetOpen(true);
        },
        [isMobile, setSelectedEndpoint],
    );

    const handleCloseSlide = useCallback(() => {
        setSelectedEndpoint(null);
    }, [setSelectedEndpoint]);

    const handleNavigate = useCallback(
        (anchor: string, schemaId?: string | null) => {
            // In selector mode a schema switch may be required before the
            // anchor exists in the DOM — defer the scroll until the next
            // paint so ``useOpenApiSchema`` has a chance to swap endpoints.
            if (schemaId && schemaId !== currentSchema?.id && grouping === 'selector') {
                setCurrentSchema(schemaId);
                requestAnimationFrame(() => {
                    docsRef.current?.scrollToAnchor(anchor);
                });
                return;
            }
            docsRef.current?.scrollToAnchor(anchor);
        },
        [currentSchema?.id, grouping, setCurrentSchema],
    );

    const handleActiveChange = useCallback((anchor: string | null, schemaId: string | null) => {
        setActiveAnchor(anchor);
        setActiveSchemaId(schemaId);
    }, []);

    // URL sync: read hash on mount / popstate → apply; write hash when
    // scrollspy updates. Only the *effective* active schema goes into the
    // hash — in ``selector`` mode it's the combobox value, in ``sections``
    // mode it's whichever schema the scrollspy is currently inside.
    const effectiveSchemaId = grouping === 'sections' ? activeSchemaId : currentSchema?.id ?? null;

    const handleHashTarget = useCallback(
        (target: ParsedHash) => {
            if (!target.schemaId && !target.anchor) return;

            // Schema-id segment may be either the raw id or a slug — match
            // both so copy-pasted URLs survive id changes that don't affect
            // the slug. First match wins.
            const matched = target.schemaId
                ? schemas.find((s) => s.id === target.schemaId || slugifySchemaId(s.id) === target.schemaId)
                : null;

            const needsSchemaSwitch =
                matched && grouping === 'selector' && matched.id !== currentSchema?.id;

            if (needsSchemaSwitch) {
                setCurrentSchema(matched.id);
            }

            if (target.anchor) {
                const anchor = target.anchor;
                // Wait one frame when a switch happened so the new DOM exists.
                if (needsSchemaSwitch) {
                    requestAnimationFrame(() => {
                        docsRef.current?.scrollToAnchor(anchor);
                    });
                } else {
                    docsRef.current?.scrollToAnchor(anchor);
                }
            }
        },
        [schemas, grouping, currentSchema?.id, setCurrentSchema],
    );

    useDocsUrlSync({
        enabled: urlSyncEnabled,
        currentSchemaId: effectiveSchemaId,
        activeAnchor,
        onHashTarget: handleHashTarget,
    });

    // ─── Loading / error branches ─────────────────────────────────────────

    if (loading) {
        return (
            <div className="grid grid-cols-[260px_1fr] items-start">
                <div
                    className="sticky top-[var(--navbar-height,64px)] border-r p-3 space-y-1.5 overflow-y-auto"
                    style={{ height: 'calc(100dvh - var(--navbar-height, 64px))' }}
                >
                    {Array.from({ length: 12 }).map((_, i) => (
                        <Skeleton key={i} className="h-8 w-full rounded" />
                    ))}
                </div>
                <div className="p-8 space-y-4">
                    <Skeleton className="h-8 w-1/2" />
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-3/4" />
                    <div className="mt-8 space-y-6">
                        {Array.from({ length: 3 }).map((_, i) => (
                            <div key={i} className="space-y-3">
                                <Skeleton className="h-6 w-1/3" />
                                <Skeleton className="h-20 w-full" />
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div
                className="flex items-center justify-center p-8"
                style={{ height: 'calc(100dvh - var(--navbar-height, 64px))' }}
            >
                <p className="text-sm text-destructive">Failed to load schema: {error}</p>
            </div>
        );
    }

    // ─── Mobile: sidebar + docs only, playground opens in sheet ───────────

    if (isMobile) {
        return (
            <div className="flex flex-col">
                <EndpointDraftSync schemaId={currentSchema?.id ?? null} />
                {grouping === 'sections' ? (
                    <DocsView
                        ref={docsRef}
                        grouping="sections"
                        schemasData={schemasData}
                        selectedVersion={state.selectedVersion}
                        loadedEndpoint={state.selectedEndpoint}
                        onTryEndpoint={handleTry}
                        onActiveChange={handleActiveChange}
                    />
                ) : (
                    <DocsView
                        ref={docsRef}
                        info={schemaInfo}
                        rawSchema={rawSchema}
                        resolvedBaseUrl={resolvedBaseUrl}
                        endpoints={endpoints}
                        selectedVersion={state.selectedVersion}
                        loadedEndpoint={state.selectedEndpoint}
                        onTryEndpoint={handleTry}
                        onActiveChange={handleActiveChange}
                    />
                )}
                <TryItSheet open={sheetOpen} onOpenChange={setSheetOpen} />
            </div>
        );
    }

    // ─── Desktop ──────────────────────────────────────────────────────────

    return (
        <div className="grid grid-cols-[260px_minmax(0,1fr)] items-start">
                <EndpointDraftSync schemaId={currentSchema?.id ?? null} />
                <div
                    className="sticky top-[var(--navbar-height,64px)]"
                    style={{ height: 'calc(100dvh - var(--navbar-height, 64px))' }}
                >
                    <DocsSidebar
                        info={schemaInfo}
                        endpoints={endpoints}
                        schemas={schemas}
                        currentSchemaId={currentSchema?.id ?? null}
                        onSchemaChange={setCurrentSchema}
                        activeEndpointId={activeAnchor}
                        selectedVersion={state.selectedVersion}
                        onNavigate={handleNavigate}
                        grouping={grouping}
                        endpointsBySchema={endpointsBySchema}
                        rawSchema={rawSchema}
                        resolvedBaseUrl={resolvedBaseUrl}
                    />
                </div>
                {grouping === 'sections' ? (
                    <DocsView
                        ref={docsRef}
                        grouping="sections"
                        schemasData={schemasData}
                        selectedVersion={state.selectedVersion}
                        loadedEndpoint={state.selectedEndpoint}
                        onTryEndpoint={handleTry}
                        onActiveChange={handleActiveChange}
                    />
                ) : (
                    <DocsView
                        ref={docsRef}
                        info={schemaInfo}
                        rawSchema={rawSchema}
                        resolvedBaseUrl={resolvedBaseUrl}
                        endpoints={endpoints}
                        selectedVersion={state.selectedVersion}
                        loadedEndpoint={state.selectedEndpoint}
                        onTryEndpoint={handleTry}
                        onActiveChange={handleActiveChange}
                    />
                )}
                {/* SidePanel renders into <body> via portal, so it floats
                    above the whole layout (sidebar + navbar included). */}
                <SlideInPlayground open={slideOpen} onClose={handleCloseSlide} />
            </div>
    );
};

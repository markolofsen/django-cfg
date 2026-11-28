'use client';

import React, { useCallback, useEffect, useMemo, useRef } from 'react';

import type { ApiEndpoint, LoadedSchemaEntry, OpenApiInfo, OpenApiSchema } from '../../types';
import {
    getScrollParent,
    getScrollTop,
    getTargetTop,
    getViewportHeight,
    scrollTargetTo,
    type ScrollTarget,
} from '../../utils/scrollParent';
import { deduplicateEndpoints } from '../../utils/versionManager';
import { ApiIntroSection } from './ApiIntroSection';
import { EndpointDoc } from './EndpointDoc';
import { useSectionHashRouter } from './EndpointDoc/hooks/useSectionHash';
import { SchemaCopyMenu } from './SchemaCopyMenu';

export interface DocsViewHandle {
    scrollToAnchor: (anchor: string) => void;
}

// ─── Props ───────────────────────────────────────────────────────────────────

interface SelectorProps {
    grouping?: 'selector';
    info: OpenApiInfo | null;
    rawSchema: OpenApiSchema | null;
    resolvedBaseUrl?: string;
    endpoints: ApiEndpoint[];
    selectedVersion: string;
    loadedEndpoint: ApiEndpoint | null;
    onTryEndpoint: (ep: ApiEndpoint) => void;
    onActiveChange: (anchor: string | null, schemaId: string | null) => void;
}

interface SectionsProps {
    grouping: 'sections';
    /** Per-schema data (info + endpoints). Rendered in order. */
    schemasData: LoadedSchemaEntry[];
    selectedVersion: string;
    loadedEndpoint: ApiEndpoint | null;
    onTryEndpoint: (ep: ApiEndpoint) => void;
    onActiveChange: (anchor: string | null, schemaId: string | null) => void;
}

type DocsViewProps = SelectorProps | SectionsProps;

// ─── View-model types ────────────────────────────────────────────────────────

interface EndpointRow {
    key: string;
    endpoint: ApiEndpoint;
    isLoaded: boolean;
    schemaId: string | null;
}

type SectionState =
    | { kind: 'ready'; rows: EndpointRow[] }
    | { kind: 'loading' }
    | { kind: 'error'; message: string }
    | { kind: 'empty' };

interface SchemaSectionVM {
    schemaId: string;
    title: string;
    version: string | null;
    description: string | null;
    state: SectionState;
    /** Copy-for-AI payload. ``null`` when the section is still loading
     *  or failed — the dropdown stays disabled. */
    rawSchema: OpenApiSchema | null;
    baseUrl: string | undefined;
    allEndpoints: ApiEndpoint[];
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Pixel offset from the top of the scroll container where the viewer
 *  should "park" sections. Reads ``--navbar-height`` for back-compat
 *  with pages that already set it; defaults to ``0`` for embedded /
 *  no-navbar setups (the common case when hosted in a shell). */
const readNavbarOffset = () => {
    if (typeof document === 'undefined') return 0;
    const raw = getComputedStyle(document.documentElement).getPropertyValue('--navbar-height');
    const parsed = parseInt(raw || '', 10);
    return Number.isFinite(parsed) ? parsed : 0;
};

const isSameEndpoint = (a: ApiEndpoint | null, b: ApiEndpoint) =>
    a !== null && a.method === b.method && a.path === b.path;

function buildEndpointRow(
    ep: ApiEndpoint,
    loadedEndpoint: ApiEndpoint | null,
    schemaId: string | null,
): EndpointRow {
    const keySchema = schemaId ? `${schemaId}-` : '';
    return {
        key: `${keySchema}${ep.method}-${ep.path}`,
        endpoint: ep,
        isLoaded: isSameEndpoint(loadedEndpoint, ep),
        schemaId,
    };
}

function buildSchemaSectionVM(
    entry: LoadedSchemaEntry,
    selectedVersion: string,
    loadedEndpoint: ApiEndpoint | null,
): SchemaSectionVM {
    const title = entry.info?.title ?? entry.source.name;
    const version = entry.info?.version ?? null;
    const description = entry.info?.description ?? null;

    let state: SectionState;
    if (entry.loading) {
        state = { kind: 'loading' };
    } else if (entry.error) {
        state = { kind: 'error', message: entry.error };
    } else {
        const visible = deduplicateEndpoints(entry.endpoints, selectedVersion);
        state = visible.length === 0
            ? { kind: 'empty' }
            : {
                kind: 'ready',
                rows: visible.map((ep) => buildEndpointRow(ep, loadedEndpoint, entry.source.id)),
            };
    }

    return {
        schemaId: entry.source.id,
        title,
        version,
        description,
        state,
        rawSchema: entry.rawSchema,
        baseUrl: entry.resolvedBaseUrl,
        allEndpoints: entry.endpoints,
    };
}

// ─── Component ───────────────────────────────────────────────────────────────

export const DocsView = React.forwardRef<DocsViewHandle, DocsViewProps>(function DocsView(
    props,
    ref,
) {
    const scrollRef = useRef<HTMLDivElement | null>(null);
    const scrollTargetRef = useRef<ScrollTarget | null>(null);
    const { onActiveChange } = props;

    // ``#section=<endpointId>.<sectionId>`` shareable deep-links —
    // opens the referenced section in the store and scrolls it in.
    // Idempotent, attaches a single hashchange listener.
    useSectionHashRouter();

    // Resolve the real scroll container once the ref is attached. In
    // standalone pages that's ``window``; inside an ``overflow-auto``
    // shell (dev playground, modal) it's the wrapping DIV.
    const ensureScrollTarget = useCallback((): ScrollTarget | null => {
        if (scrollTargetRef.current) return scrollTargetRef.current;
        if (!scrollRef.current) return null;
        scrollTargetRef.current = getScrollParent(scrollRef.current);
        return scrollTargetRef.current;
    }, []);

    // Scroll a given section into view. Works against whichever ancestor
    // actually scrolls — window for standalone, the overflow-auto parent
    // for embedded layouts — so callers don't need to know the difference.
    const scrollToAnchor = useCallback(
        (anchor: string) => {
            const root = scrollRef.current;
            if (!root) return;
            const el = root.querySelector<HTMLElement>(`[data-endpoint-anchor="${anchor}"]`);
            if (!el) return;
            const target = ensureScrollTarget();
            if (!target) return;
            const navbar = readNavbarOffset();
            const top =
                el.getBoundingClientRect().top -
                getTargetTop(target) +
                getScrollTop(target) -
                navbar -
                8;
            scrollTargetTo(target, top);
        },
        [ensureScrollTarget],
    );

    React.useImperativeHandle(ref, () => ({ scrollToAnchor }), [scrollToAnchor]);

    // Scrollspy: pick the topmost endpoint section whose top is near the
    // upper quarter of the viewport. Listens on the real scroll container
    // (see ``ensureScrollTarget``) because ``scroll`` events on a nested
    // overflow:auto element do NOT bubble up to window.
    useEffect(() => {
        const root = scrollRef.current;
        if (!root) return;
        const target = ensureScrollTarget();
        if (!target) return;

        let rafId = 0;
        let lastActive: string | null = null;

        const compute = () => {
            rafId = 0;
            const sections = root.querySelectorAll<HTMLElement>('[data-endpoint-anchor]');
            if (sections.length === 0) return;
            const navbar = readNavbarOffset();
            const viewportTop = getTargetTop(target);
            const threshold = viewportTop + navbar + getViewportHeight(target) * 0.25;
            let active: HTMLElement | null = null;
            for (const s of Array.from(sections)) {
                const top = s.getBoundingClientRect().top;
                if (top <= threshold) {
                    active = s;
                } else {
                    break;
                }
            }
            const anchor = active?.dataset.endpointAnchor ?? null;
            if (anchor !== lastActive) {
                lastActive = anchor;
                onActiveChange(anchor, active?.dataset.schemaId || null);
            }
        };

        const onScroll = () => {
            if (rafId) return;
            rafId = requestAnimationFrame(compute);
        };

        compute();
        target.addEventListener('scroll', onScroll, { passive: true });
        // Resize always bubbles to window — listen there regardless of target.
        window.addEventListener('resize', onScroll, { passive: true });
        return () => {
            target.removeEventListener('scroll', onScroll);
            window.removeEventListener('resize', onScroll);
            if (rafId) cancelAnimationFrame(rafId);
        };
    }, [onActiveChange, ensureScrollTarget, props]);

    if (props.grouping === 'sections') {
        return <SectionsBody scrollRef={scrollRef} {...props} />;
    }

    return <SelectorBody scrollRef={scrollRef} {...props} />;
});

// ─── Selector body (single active schema) ────────────────────────────────────

function SelectorBody({
    scrollRef,
    info,
    rawSchema,
    resolvedBaseUrl,
    endpoints,
    selectedVersion,
    loadedEndpoint,
    onTryEndpoint,
}: SelectorProps & { scrollRef: React.RefObject<HTMLDivElement | null> }) {
    const visibleEndpoints = useMemo(
        () => deduplicateEndpoints(endpoints, selectedVersion),
        [endpoints, selectedVersion],
    );

    const rows = useMemo<EndpointRow[]>(
        () => visibleEndpoints.map((ep) => buildEndpointRow(ep, loadedEndpoint, ep.schemaId ?? null)),
        [visibleEndpoints, loadedEndpoint],
    );

    const isEmpty = rows.length === 0;

    return (
        <div ref={scrollRef}>
            <div className="mx-auto w-full max-w-[860px] px-6 md:px-10 lg:px-14 py-12">
                {info && (
                    <ApiIntroSection
                        info={info}
                        schema={rawSchema}
                        endpoints={visibleEndpoints}
                        resolvedBaseUrl={resolvedBaseUrl}
                    />
                )}
                {isEmpty ? (
                    <div className="py-16 text-center text-sm text-muted-foreground">
                        No endpoints to display.
                    </div>
                ) : (
                    <div className="divide-y divide-border/60">
                        {rows.map((row) => (
                            <EndpointDoc
                                key={row.key}
                                endpoint={row.endpoint}
                                isLoadedInPlayground={row.isLoaded}
                                onTryIt={() => onTryEndpoint(row.endpoint)}
                                schemaId={row.schemaId}
                            />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

// ─── Sections body (all schemas concatenated) ────────────────────────────────

function SectionsBody({
    scrollRef,
    schemasData,
    selectedVersion,
    loadedEndpoint,
    onTryEndpoint,
}: SectionsProps & { scrollRef: React.RefObject<HTMLDivElement | null> }) {
    const sections = useMemo<SchemaSectionVM[]>(
        () => schemasData.map((e) => buildSchemaSectionVM(e, selectedVersion, loadedEndpoint)),
        [schemasData, selectedVersion, loadedEndpoint],
    );

    return (
        <div ref={scrollRef}>
            <div className="mx-auto w-full max-w-[860px] px-6 md:px-10 lg:px-14 py-12 space-y-16">
                {sections.map((section) => (
                    <SchemaSectionView key={section.schemaId} section={section} onTryEndpoint={onTryEndpoint} />
                ))}
            </div>
        </div>
    );
}

const SchemaSectionView = React.memo(function SchemaSectionView({
    section,
    onTryEndpoint,
}: {
    section: SchemaSectionVM;
    onTryEndpoint: (ep: ApiEndpoint) => void;
}) {
    const canCopy = section.rawSchema !== null && section.allEndpoints.length > 0;
    return (
        <section data-schema-anchor={section.schemaId} className="scroll-mt-20">
            <header className="mb-8 pb-4 border-b">
                <div className="flex items-start justify-between gap-4">
                    <div className="flex items-baseline gap-3 min-w-0">
                        <h2 className="text-2xl font-semibold tracking-tight">{section.title}</h2>
                        {section.version && (
                            <span className="font-mono text-xs text-muted-foreground/70">
                                v{section.version}
                            </span>
                        )}
                    </div>
                    {canCopy && (
                        <SchemaCopyMenu
                            schema={section.rawSchema}
                            endpoints={section.allEndpoints}
                            baseUrl={section.baseUrl}
                        />
                    )}
                </div>
                {section.description && (
                    <p className="mt-2 text-sm text-muted-foreground whitespace-pre-wrap">
                        {section.description}
                    </p>
                )}
            </header>
            <SchemaSectionStateView section={section} onTryEndpoint={onTryEndpoint} />
        </section>
    );
});

function SchemaSectionStateView({
    section,
    onTryEndpoint,
}: {
    section: SchemaSectionVM;
    onTryEndpoint: (ep: ApiEndpoint) => void;
}) {
    switch (section.state.kind) {
        case 'loading':
            return (
                <div className="py-8 text-center text-sm text-muted-foreground">
                    Loading {section.title}…
                </div>
            );
        case 'error':
            return (
                <div className="py-8 text-center text-sm text-destructive">
                    Failed to load {section.title}: {section.state.message}
                </div>
            );
        case 'empty':
            return (
                <div className="py-8 text-center text-sm text-muted-foreground">
                    No endpoints in this schema.
                </div>
            );
        case 'ready':
            return (
                <div className="divide-y divide-border/60">
                    {section.state.rows.map((row) => (
                        <EndpointDoc
                            key={row.key}
                            endpoint={row.endpoint}
                            isLoadedInPlayground={row.isLoaded}
                            onTryIt={() => onTryEndpoint(row.endpoint)}
                            schemaId={row.schemaId}
                        />
                    ))}
                </div>
            );
    }
}

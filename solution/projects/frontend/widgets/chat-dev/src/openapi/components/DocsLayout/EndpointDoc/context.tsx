'use client';

import React, { createContext, useContext, useMemo } from 'react';

/** Identity context for a single EndpointDoc subtree.
 *
 *  This is NOT a state container — state lives in the zustand store at
 *  ``./store``. The context only carries per-endpoint *identity* values
 *  so children (Section, CodeSamples, future ExpandAll button) don't
 *  have to re-derive them or receive them as repeated props.
 *
 *  Why identity-only:
 *    - One zustand singleton handles state for *all* endpoints on the
 *      page, keyed by ``endpointId``. Wrapping zustand itself in a
 *      Provider would defeat that composite-key design.
 *    - Identity (anchor, HTTP method) is invariant inside an endpoint
 *      card; deriving it per-child is wasted work and makes the props
 *      table look noisier than the logic actually is. */
interface EndpointDocContextValue {
    /** DOM-safe anchor id for this endpoint — used as the store key
     *  prefix (``openSections[`${endpointId}:${sectionId}`]``) and as
     *  the URL hash target for shareable links. */
    endpointId: string;
    /** HTTP method (``GET`` / ``POST`` / …). Drives per-method default
     *  open state for Section. Kept in context so ``defaultSectionOpen``
     *  doesn't need to be threaded as a prop through every subtree. */
    method: string;
}

const EndpointDocContext = createContext<EndpointDocContextValue | null>(null);

interface EndpointDocProviderProps extends EndpointDocContextValue {
    children: React.ReactNode;
}

export function EndpointDocProvider({ endpointId, method, children }: EndpointDocProviderProps) {
    // Memoise the value so every re-render of the parent orchestrator
    // doesn't invalidate children reading the context — the common
    // hover/focus state on the header row re-renders EndpointDoc often.
    const value = useMemo(() => ({ endpointId, method }), [endpointId, method]);
    return <EndpointDocContext.Provider value={value}>{children}</EndpointDocContext.Provider>;
}

export function useEndpointDocContext(): EndpointDocContextValue {
    const ctx = useContext(EndpointDocContext);
    if (!ctx) {
        // Treated as a programming error, not a runtime one — if this
        // fires, something rendered EndpointDoc internals outside the
        // provider, which means the store keys will collide or be
        // missing entirely. Loud failure beats silent corruption.
        throw new Error(
            '[OpenapiViewer] useEndpointDocContext must be used inside <EndpointDocProvider>.',
        );
    }
    return ctx;
}

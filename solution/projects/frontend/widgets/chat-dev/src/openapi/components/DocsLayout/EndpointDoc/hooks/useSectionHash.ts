'use client';

import { useEffect } from 'react';

import { useEndpointDocStore } from '../store';
import { ALL_SECTION_IDS, type SectionId } from '../types';

/** Parse ``#section=<endpointId>.<sectionId>`` out of a hash string.
 *  Returns ``null`` for any other shape (including the plain
 *  ``#<endpointId>`` form used elsewhere for scrolling to an endpoint). */
export function parseSectionHash(hash: string): { endpointId: string; sectionId: SectionId } | null {
    const raw = hash.startsWith('#') ? hash.slice(1) : hash;
    if (!raw.startsWith('section=')) return null;
    const value = raw.slice('section='.length);
    const dot = value.lastIndexOf('.');
    if (dot <= 0 || dot === value.length - 1) return null;
    const endpointId = value.slice(0, dot);
    const sectionIdCandidate = value.slice(dot + 1);
    if (!(ALL_SECTION_IDS as readonly string[]).includes(sectionIdCandidate)) return null;
    return { endpointId, sectionId: sectionIdCandidate as SectionId };
}

/** Build the shareable hash that opens a specific section. */
export function buildSectionHash(endpointId: string, sectionId: SectionId): string {
    return `section=${endpointId}.${sectionId}`;
}

/** On mount + on hashchange, read ``#section=...``, open that section
 *  in the store, and scroll its endpoint into view. Runs once per
 *  hash change, not per endpoint render — the effect lives above the
 *  per-endpoint level in the tree.
 *
 *  Behaviour:
 *    1. Parse hash. If it isn't our ``section=`` form, bail — the
 *       browser's own anchor-scrolling handles ``#ep-…`` URLs already.
 *    2. Open the referenced section in the zustand store so its body
 *       is visible the moment the user lands.
 *    3. Scroll the endpoint's ``<section id={endpointId}>`` into view
 *       on the next frame (after the section body has mounted). */
export function useSectionHashRouter(): void {
    const setSectionOpen = useEndpointDocStore((s) => s.setSectionOpen);

    useEffect(() => {
        if (typeof window === 'undefined') return;

        function apply() {
            const parsed = parseSectionHash(window.location.hash);
            if (!parsed) return;
            setSectionOpen(parsed.endpointId, parsed.sectionId, true);
            // Defer scroll to let the section body render first —
            // scrolling a collapsed row lands on the wrong offset
            // because the body takes vertical space once expanded.
            requestAnimationFrame(() => {
                const el = document.getElementById(parsed.endpointId);
                el?.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        }

        apply();
        window.addEventListener('hashchange', apply);
        return () => window.removeEventListener('hashchange', apply);
    }, [setSectionOpen]);
}

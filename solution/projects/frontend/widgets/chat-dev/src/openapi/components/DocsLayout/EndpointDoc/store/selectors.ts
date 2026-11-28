'use client';

import type { CodeSampleTargetId } from '../../../../utils/codeSamples';
import type { SectionId } from '../types';
import { sectionKey, useEndpointDocStore } from './index';

/** Read whether a section is open, falling back to ``defaultOpen`` when
 *  the user hasn't explicitly toggled it. Returning a raw boolean makes
 *  the caller's conditional rendering trivial. */
export function useIsSectionOpen(
    endpointId: string,
    sectionId: SectionId,
    defaultOpen: boolean,
): boolean {
    return useEndpointDocStore((s) => {
        const explicit = s.openSections[sectionKey(endpointId, sectionId)];
        return explicit === undefined ? defaultOpen : explicit;
    });
}

/** Read the active code-sample tab for this endpoint, falling back to
 *  a shared default (``curl``). Falls back at read time rather than at
 *  write time so changing the default later doesn't require store
 *  migration. */
export function useActiveCodeTab(
    endpointId: string,
    fallback: CodeSampleTargetId = 'curl',
): CodeSampleTargetId {
    return useEndpointDocStore((s) => s.activeCodeTab[endpointId] ?? fallback);
}

export function useEndpointDocActions() {
    return useEndpointDocStore((s) => ({
        toggleSection: s.toggleSection,
        setSectionOpen: s.setSectionOpen,
        setCodeTab: s.setCodeTab,
        expandAll: s.expandAll,
        collapseAll: s.collapseAll,
    }));
}

'use client';

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

import type { CodeSampleTargetId } from '../../../../utils/codeSamples';
import type { SectionId } from '../types';
import { CFG_KEYS } from '@djangocfg/api/storage';

/** Composite key so the same section id (``responses``) can have
 *  distinct state per endpoint on the page. We don't use Map because
 *  zustand+persist serialises state to JSON and Map survival there
 *  requires extra replacer/reviver boilerplate for no real gain. */
export const sectionKey = (endpointId: string, sectionId: SectionId): string =>
    `${endpointId}:${sectionId}`;

export interface EndpointDocState {
    /** ``${endpointId}:${sectionId}`` → open? — ``undefined`` means
     *  "use the component's ``defaultOpen``"; the store only stores
     *  user-driven overrides so defaults can change later without
     *  stale persisted state overriding them. */
    openSections: Record<string, boolean>;
    /** Active code-sample tab per endpoint. Keyed on endpoint id only;
     *  users tend to pick one language and stick with it across the
     *  whole page, so sharing between endpoints is acceptable UX. */
    activeCodeTab: Record<string, CodeSampleTargetId>;
}

export interface EndpointDocActions {
    /** Flip the section's open state. ``defaultOpen`` is the value the
     *  ``Section`` component currently shows when the user has no
     *  explicit override yet — passing it in lets the first click
     *  always invert what's actually on screen, instead of always
     *  setting ``false`` (which silently no-ops when the section was
     *  closed by default). */
    toggleSection: (endpointId: string, sectionId: SectionId, defaultOpen: boolean) => void;
    setSectionOpen: (endpointId: string, sectionId: SectionId, open: boolean) => void;
    setCodeTab: (endpointId: string, tab: CodeSampleTargetId) => void;
    /** Bulk ops — "expand all" / "collapse all" on a single endpoint.
     *  The component calls these from an action button in the header. */
    expandAll: (endpointId: string, sectionIds: readonly SectionId[]) => void;
    collapseAll: (endpointId: string, sectionIds: readonly SectionId[]) => void;
}

export type EndpointDocStore = EndpointDocState & EndpointDocActions;

const initialState: EndpointDocState = {
    openSections: {},
    activeCodeTab: {},
};

/** Zustand store with sessionStorage persistence. Using sessionStorage
 *  (not localStorage) so closing the tab clears state — the viewer is
 *  often embedded in a dashboard and persisting forever would surprise
 *  users who switched schemas. */
export const useEndpointDocStore = create<EndpointDocStore>()(
    persist(
        (set) => ({
            ...initialState,

            toggleSection: (endpointId, sectionId, defaultOpen) =>
                set((state) => {
                    const key = sectionKey(endpointId, sectionId);
                    const current = state.openSections[key];
                    const visible = current === undefined ? defaultOpen : current;
                    return {
                        openSections: {
                            ...state.openSections,
                            [key]: !visible,
                        },
                    };
                }),

            setSectionOpen: (endpointId, sectionId, open) =>
                set((state) => ({
                    openSections: {
                        ...state.openSections,
                        [sectionKey(endpointId, sectionId)]: open,
                    },
                })),

            setCodeTab: (endpointId, tab) =>
                set((state) => ({
                    activeCodeTab: {
                        ...state.activeCodeTab,
                        [endpointId]: tab,
                    },
                })),

            expandAll: (endpointId, sectionIds) =>
                set((state) => {
                    const next = { ...state.openSections };
                    for (const sid of sectionIds) {
                        next[sectionKey(endpointId, sid)] = true;
                    }
                    return { openSections: next };
                }),

            collapseAll: (endpointId, sectionIds) =>
                set((state) => {
                    const next = { ...state.openSections };
                    for (const sid of sectionIds) {
                        next[sectionKey(endpointId, sid)] = false;
                    }
                    return { openSections: next };
                }),
        }),
        {
            name: CFG_KEYS.agentEndpointDoc.key,
            storage: createJSONStorage(() => {
                // Guard for SSR / non-browser environments — zustand's
                // persist middleware calls storage.getItem synchronously
                // during hydration, and ``sessionStorage`` is undefined
                // there. Returning a noop keeps SSR snapshots stable.
                if (typeof window === 'undefined') {
                    return {
                        getItem: () => null,
                        setItem: () => {},
                        removeItem: () => {},
                    };
                }
                return window.sessionStorage;
            }),
            // Only persist user overrides, not the functions. Zustand
            // serialises everything by default and logs a warning on
            // non-serialisable values; partialize keeps the payload lean.
            partialize: (state) => ({
                openSections: state.openSections,
                activeCodeTab: state.activeCodeTab,
            }),
        },
    ),
);

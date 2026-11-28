import type { ApiEndpoint } from '../../../types';

/** HTTP method filter. ``ALL`` is a sentinel for no filter — using a
 *  string union (rather than ``string | null``) keeps the filter chips
 *  and reducer logic type-safe without null juggling. */
export const METHOD_FILTERS = ['ALL', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'] as const;
export type MethodFilter = (typeof METHOD_FILTERS)[number];

export interface EndpointRowVM {
    key: string;
    anchor: string;
    schemaId: string | null;
    label: string;
    tooltip: string;
    method: string;
    /** Summary-less endpoints get a monospace font for the path-tail
     *  label so the tech string is readable against a sea of prose. */
    useMono: boolean;
    isActive: boolean;
}

export interface CategoryVM {
    key: string;
    category: string;
    rows: EndpointRowVM[];
}

export interface SchemaSectionVM {
    sourceId: string;
    sourceName: string;
    categories: CategoryVM[];
}

export type SidebarBodyVM =
    | { kind: 'flat'; categories: CategoryVM[]; emptyText: string }
    | { kind: 'sections'; sections: SchemaSectionVM[]; emptyText: string };

export type NavigateFn = (anchor: string, schemaId?: string | null) => void;

// Re-exported here so downstream files don't all re-import from the
// outer ``types`` module for every component prop.
export type { ApiEndpoint };

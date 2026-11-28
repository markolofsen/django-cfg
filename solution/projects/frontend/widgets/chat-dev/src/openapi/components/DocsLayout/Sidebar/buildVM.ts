import type { ApiEndpoint, OpenApiSchema, SchemaSource } from '../../../types';
import { deduplicateEndpoints } from '../../../utils/versionManager';
import { endpointAnchor } from '../anchor';
import { buildSchemaSections, groupEndpoints, type EndpointGroup } from '../grouping';
import { sidebarLabel, sidebarTooltip } from '../sidebarLabel';
import type {
    CategoryVM,
    EndpointRowVM,
    MethodFilter,
    SchemaSectionVM,
    SidebarBodyVM,
} from './types';

// ``OpenApiSchema`` is imported to satisfy the build VM signatures even
// though we never read it here — re-exported so consumers can reuse
// the same type surface without another import.
export type { OpenApiSchema };

export function filterEndpoints(
    list: ApiEndpoint[],
    query: string,
    method: MethodFilter,
): ApiEndpoint[] {
    let out = list;
    if (method !== 'ALL') {
        out = out.filter((e) => e.method === method);
    }
    if (query) {
        const q = query.toLowerCase();
        out = out.filter(
            (e) =>
                e.summary.toLowerCase().includes(q) ||
                e.name.toLowerCase().includes(q) ||
                e.description.toLowerCase().includes(q) ||
                e.path.toLowerCase().includes(q),
        );
    }
    return out;
}

function buildCategory(
    group: EndpointGroup,
    activeEndpointId: string | null,
    schemaId: string | null,
    keyPrefix: string,
): CategoryVM {
    const rows: EndpointRowVM[] = group.endpoints.map((ep) => {
        const anchor = endpointAnchor(ep, schemaId ?? ep.schemaId ?? null);
        return {
            key: `${ep.method}-${ep.path}`,
            anchor,
            schemaId: schemaId ?? ep.schemaId ?? null,
            label: sidebarLabel(ep, group.commonPrefix),
            tooltip: sidebarTooltip(ep),
            method: ep.method,
            useMono: !ep.summary,
            isActive: activeEndpointId === anchor,
        };
    });
    return {
        key: `${keyPrefix}${group.category}`,
        category: group.category,
        rows,
    };
}

function emptyTextFor(query: string, method: MethodFilter, defaultText: string): string {
    if (query && method !== 'ALL') return `No ${method} endpoints match "${query}"`;
    if (query) return `No endpoints match "${query}"`;
    if (method !== 'ALL') return `No ${method} endpoints`;
    return defaultText;
}

export function buildFlatVM(
    endpoints: ApiEndpoint[],
    selectedVersion: string,
    query: string,
    method: MethodFilter,
    activeEndpointId: string | null,
): SidebarBodyVM {
    const filtered = filterEndpoints(
        deduplicateEndpoints(endpoints, selectedVersion),
        query,
        method,
    );
    const groups = groupEndpoints(filtered);
    return {
        kind: 'flat',
        categories: groups.map((g) => buildCategory(g, activeEndpointId, null, '')),
        emptyText: emptyTextFor(query, method, 'No endpoints in this schema'),
    };
}

export function buildSectionsVM(
    schemas: SchemaSource[],
    endpointsBySchema: Record<string, ApiEndpoint[]>,
    selectedVersion: string,
    query: string,
    method: MethodFilter,
    activeEndpointId: string | null,
): SidebarBodyVM {
    const filteredMap: Record<string, ApiEndpoint[]> = {};
    for (const src of schemas) {
        const raw = endpointsBySchema[src.id] ?? [];
        filteredMap[src.id] = filterEndpoints(
            deduplicateEndpoints(raw, selectedVersion),
            query,
            method,
        );
    }
    const rawSections = buildSchemaSections(schemas, filteredMap);
    const sections: SchemaSectionVM[] = rawSections
        .filter((s) => s.groups.length > 0)
        .map((s) => ({
            sourceId: s.source.id,
            sourceName: s.source.name,
            categories: s.groups.map((g) =>
                buildCategory(g, activeEndpointId, s.source.id, `${s.source.id}-`),
            ),
        }));
    return {
        kind: 'sections',
        sections,
        emptyText: emptyTextFor(query, method, 'No endpoints in any schema'),
    };
}

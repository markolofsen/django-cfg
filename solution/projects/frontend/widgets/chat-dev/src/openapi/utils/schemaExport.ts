/**
 * Export the current OpenAPI schema in formats friendly for LLM agents.
 *
 * Three flavours:
 *   - raw:      JSON.stringify(schema) — full fidelity, largest.
 *   - compact:  dereferenced + pruned (no xml/examples, short descriptions,
 *               no whitespace). Usually 30–50% of raw.
 *   - markdown: prose summary of endpoints + params + responses. Smallest,
 *               best for small prompts. Drops response body schemas.
 *
 * Per-endpoint markdown is also exported so a Copy-for-AI button on a
 * single endpoint stays cheap and does not leak unrelated paths.
 *
 * ``baseUrl`` resolution is done by the caller; we just substitute the
 * resolved value into ``servers[0]`` so the copied schema points at the
 * live API, not at whatever ``schema.servers`` originally held.
 */

import type { ApiEndpoint, OpenApiSchema } from '../types';
import { relativePath, resolveBaseUrl } from './url';

// ─── Dereference ──────────────────────────────────────────────────────────────

/**
 * Walk a JSON object and replace every ``$ref`` with the resolved value.
 *
 * Cycle handling: each ``$ref`` currently being expanded is tracked on an
 * active set. If a ref points back into a ref already on the stack, the
 * ``$ref`` node is left intact instead of being inlined — downstream
 * consumers (``openapi-sampler``) resolve it against the raw spec, so a
 * left-over local ref is harmless and far cheaper than inlining a
 * recursive type ``maxDepth`` levels deep. ``maxDepth`` is still a hard
 * backstop for pathologically wide graphs.
 */
export function dereferenceSchema(schema: OpenApiSchema, maxDepth = 50): OpenApiSchema {
    const root = schema as unknown as Record<string, unknown>;

    function resolveRef(ref: string): unknown {
        // Only handle local refs (#/components/schemas/Foo). External refs are
        // out of scope — the schema we have in memory is already a single file.
        if (!ref.startsWith('#/')) return null;
        // JSON Pointer un-escaping: ``~1`` → ``/``, ``~0`` → ``~`` (then
        // percent-decoding) so component names with slashes resolve.
        const parts = ref
            .slice(2)
            .split('/')
            .map((p) => decodeURIComponent(p.replace(/~1/g, '/').replace(/~0/g, '~')));
        let node: unknown = root;
        for (const part of parts) {
            if (node && typeof node === 'object' && part in (node as Record<string, unknown>)) {
                node = (node as Record<string, unknown>)[part];
            } else {
                return null;
            }
        }
        return node;
    }

    // Refs currently mid-expansion — detects ``A → B → A`` cycles.
    const active = new Set<string>();

    function walk(value: unknown, depth: number): unknown {
        if (depth > maxDepth) return value;
        if (Array.isArray(value)) return value.map((v) => walk(v, depth + 1));
        if (value && typeof value === 'object') {
            const obj = value as Record<string, unknown>;
            if (typeof obj.$ref === 'string') {
                const ref = obj.$ref;
                // Cycle — keep the ref node so the sampler can resolve it.
                if (active.has(ref)) return obj;
                const resolved = resolveRef(ref);
                if (resolved === null) return obj;
                active.add(ref);
                const out = walk(resolved, depth + 1);
                active.delete(ref);
                return out;
            }
            const out: Record<string, unknown> = {};
            for (const [k, v] of Object.entries(obj)) out[k] = walk(v, depth + 1);
            return out;
        }
        return value;
    }

    return walk(schema, 0) as OpenApiSchema;
}

// ─── Pruning helpers ──────────────────────────────────────────────────────────

const NOISY_KEYS = new Set(['xml', 'example', 'examples', 'externalDocs']);
const MAX_DESCRIPTION_LEN = 500;

/**
 * In-place-friendly pruner (returns a new tree). Drops keys that only
 * add bytes without giving the LLM new semantic info, and truncates
 * very long prose descriptions.
 */
function pruneForCompact(value: unknown): unknown {
    if (Array.isArray(value)) return value.map(pruneForCompact);
    if (value && typeof value === 'object') {
        const out: Record<string, unknown> = {};
        for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
            if (NOISY_KEYS.has(k)) continue;
            if (k === 'description' && typeof v === 'string' && v.length > MAX_DESCRIPTION_LEN) {
                out[k] = v.slice(0, MAX_DESCRIPTION_LEN).trimEnd() + '…';
                continue;
            }
            out[k] = pruneForCompact(v);
        }
        return out;
    }
    return value;
}

// ─── Public API ───────────────────────────────────────────────────────────────

/** Overwrite ``servers[0]`` with the resolved base URL if provided. */
function withResolvedBaseUrl(schema: OpenApiSchema, baseUrl: string | undefined): OpenApiSchema {
    if (!baseUrl) return schema;
    return { ...schema, servers: [{ url: baseUrl }] };
}

export function toRawJson(schema: OpenApiSchema, baseUrl?: string): string {
    return JSON.stringify(withResolvedBaseUrl(schema, baseUrl), null, 2);
}

export function toCompactJson(schema: OpenApiSchema, baseUrl?: string): string {
    const resolved = dereferenceSchema(withResolvedBaseUrl(schema, baseUrl));
    const pruned = pruneForCompact(resolved);
    return JSON.stringify(pruned);
}

// ─── Markdown ────────────────────────────────────────────────────────────────


export function endpointToMarkdown(ep: ApiEndpoint): string {
    const lines: string[] = [];
    lines.push(`### ${ep.method} ${ep.path}`);
    if (ep.description) lines.push(ep.description);

    const pathParams = ep.parameters?.filter((p) => ep.path.includes(`{${p.name}}`)) ?? [];
    const queryParams = ep.parameters?.filter((p) => !ep.path.includes(`{${p.name}}`)) ?? [];

    if (pathParams.length > 0) {
        lines.push('', '**Path parameters**');
        for (const p of pathParams) {
            const req = p.required ? ' (required)' : '';
            const desc = p.description ? ` — ${p.description}` : '';
            lines.push(`- \`${p.name}\`: ${p.type}${req}${desc}`);
        }
    }
    if (queryParams.length > 0) {
        lines.push('', '**Query parameters**');
        for (const p of queryParams) {
            const req = p.required ? ' (required)' : '';
            const desc = p.description ? ` — ${p.description}` : '';
            lines.push(`- \`${p.name}\`: ${p.type}${req}${desc}`);
        }
    }
    if (ep.requestBody) {
        const desc = ep.requestBody.description ? ` — ${ep.requestBody.description}` : '';
        lines.push('', `**Request body:** ${ep.requestBody.type}${desc}`);
    }
    if (ep.responses && ep.responses.length > 0) {
        lines.push('', '**Responses**');
        for (const r of ep.responses) {
            lines.push(`- \`${r.code}\` — ${r.description}`);
        }
    }
    return lines.join('\n');
}

export function toMarkdown(
    schema: OpenApiSchema,
    endpoints: ApiEndpoint[],
    baseUrl?: string,
): string {
    const lines: string[] = [];
    const info = schema.info;
    const resolvedBase = resolveBaseUrl({
        config: baseUrl,
        fromServers: schema.servers?.[0]?.url,
    });

    lines.push(`# ${info?.title ?? 'API'}${info?.version ? ` (v${info.version})` : ''}`);
    if (resolvedBase) lines.push('', `**Base URL:** \`${resolvedBase}\``);
    if (info?.description) lines.push('', info.description.trim());

    // Group by tag/category for readable output.
    const grouped = new Map<string, ApiEndpoint[]>();
    for (const ep of endpoints) {
        const arr = grouped.get(ep.category) ?? [];
        arr.push(ep);
        grouped.set(ep.category, arr);
    }

    const categories = Array.from(grouped.keys()).sort((a, b) => {
        if (a === 'Other') return 1;
        if (b === 'Other') return -1;
        return a.localeCompare(b);
    });

    for (const category of categories) {
        lines.push('', `## ${category}`);
        const list = grouped.get(category)!;
        for (const ep of list) {
            // Use relativePath for section headers to keep markdown compact —
            // the full URL is already available as "Base URL" above.
            const displayPath = relativePath(ep.path);
            const sub = endpointToMarkdown({ ...ep, path: displayPath });
            lines.push('', sub);
        }
    }

    return lines.join('\n');
}

// ─── Size helper ──────────────────────────────────────────────────────────────

/** Human-readable byte count: ``12.3 KB``, ``480 B``. */
export function formatBytes(s: string): string {
    const bytes = new Blob([s]).size;
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

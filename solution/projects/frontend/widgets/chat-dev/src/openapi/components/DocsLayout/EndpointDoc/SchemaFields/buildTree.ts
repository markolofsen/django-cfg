/**
 * JSON Schema → ``FieldNode`` tree.
 *
 *  Handles the OpenAPI 3.x subset we actually see: objects with
 *  ``properties`` + ``required``, arrays with ``items``, enums,
 *  primitives with ``format``. ``allOf`` is merged shallowly.
 *  ``oneOf`` / ``anyOf`` object branches are merged so every variant's
 *  fields are visible (union of properties); ``required`` is intersected
 *  so a field optional in one variant is not shown as globally required.
 *  Non-object unions fall back to the first branch. Upstream
 *  dereferencing (``dereferenceSchema``) resolves ``$ref`` before this runs.
 */

import type { FieldKind, FieldNode } from './types';

type JsonSchemaNode = Record<string, unknown> & {
    type?: string;
    properties?: Record<string, JsonSchemaNode>;
    required?: string[];
    items?: JsonSchemaNode;
    enum?: unknown[];
    description?: string;
    format?: string;
    allOf?: JsonSchemaNode[];
    oneOf?: JsonSchemaNode[];
    anyOf?: JsonSchemaNode[];
};

/** Hard cap on recursion so self-referential schemas can't blow the
 *  call stack. Anything this deep is unreadable in a docs view anyway. */
const MAX_DEPTH = 5;

/** Merge object branches into a single pseudo-object. Shallow merge is
 *  enough for display — deep merge would need semantic JSON Schema
 *  reasoning we don't want in a read-only viewer.
 *
 *  ``intersectRequired`` controls how ``required`` combines: ``allOf`` is
 *  a conjunction so every branch's required fields apply (union); for
 *  ``oneOf`` / ``anyOf`` a field is only truly required when *every*
 *  object branch requires it (intersection). */
function mergeObjectBranches(
    branches: JsonSchemaNode[],
    intersectRequired: boolean,
): JsonSchemaNode {
    const properties: Record<string, JsonSchemaNode> = {};
    const objectBranches = branches.filter((b) => b.properties);
    const requiredSets = objectBranches.map((b) => new Set(b.required ?? []));
    for (const b of objectBranches) {
        if (b.properties) Object.assign(properties, b.properties);
    }
    let required: string[];
    if (intersectRequired && requiredSets.length > 0) {
        const [first, ...rest] = requiredSets;
        required = [...first!].filter((k) => rest.every((s) => s.has(k)));
    } else {
        required = [...new Set(requiredSets.flatMap((s) => [...s]))];
    }
    return { type: 'object', properties, required };
}

/** True when every branch is (or describes) an object — i.e. the union
 *  can be presented as a merged property table. */
function allObjectBranches(branches: JsonSchemaNode[]): boolean {
    return branches.every((b) => b.type === 'object' || Boolean(b.properties));
}

function describeType(node: JsonSchemaNode): { label: string; kind: FieldKind } {
    if (node.type === 'array') {
        const itemLabel = node.items ? describeType(node.items).label : 'any';
        return { label: `array<${itemLabel}>`, kind: 'array' };
    }
    if (node.type === 'object' || node.properties) {
        return { label: 'object', kind: 'object' };
    }
    const base = node.type || 'any';
    if (Array.isArray(node.enum) && node.enum.length > 0) {
        return { label: `${base} enum`, kind: 'primitive' };
    }
    if (node.format) {
        return { label: `${base} (${node.format})`, kind: 'primitive' };
    }
    return { label: base, kind: 'primitive' };
}

function resolveCombinators(node: JsonSchemaNode): JsonSchemaNode {
    // ``allOf`` → conjunction merge (required is a union).
    if (Array.isArray(node.allOf) && node.allOf.length > 0) {
        return { ...mergeObjectBranches(node.allOf, false), description: node.description };
    }
    // ``oneOf`` / ``anyOf`` of objects → merge so every variant's fields
    // are visible; required intersected. Non-object unions → first branch.
    for (const key of ['oneOf', 'anyOf'] as const) {
        const branches = node[key];
        if (Array.isArray(branches) && branches.length > 0) {
            if (branches.length > 1 && allObjectBranches(branches)) {
                return { ...mergeObjectBranches(branches, true), description: node.description };
            }
            return {
                ...branches[0]!,
                description: node.description ?? branches[0]!.description,
            };
        }
    }
    return node;
}

function buildNode(
    name: string,
    schema: JsonSchemaNode,
    isRequired: boolean,
    depth: number,
): FieldNode {
    const resolved = resolveCombinators(schema);
    const { label, kind } = describeType(resolved);
    const node: FieldNode = {
        name,
        type: label,
        kind,
        required: isRequired,
        description: resolved.description,
    };

    if (Array.isArray(resolved.enum) && resolved.enum.length > 0) {
        node.enumValues = resolved.enum.map((v) => String(v));
    }

    if (depth >= MAX_DEPTH) return node;

    if (kind === 'object' && resolved.properties) {
        const required = new Set(resolved.required ?? []);
        node.children = Object.entries(resolved.properties).map(([key, child]) =>
            buildNode(key, child, required.has(key), depth + 1),
        );
    } else if (kind === 'array' && resolved.items) {
        // Synthesise a single ``[]`` child. If items are objects, the
        // child's own children will appear — so the tree reads as
        // ``tags → [] → { id, name }``.
        node.children = [buildNode('[]', resolved.items, false, depth + 1)];
    }

    return node;
}

/** Top-level entry. The root schema is usually an object or array; we
 *  return its children directly so the tree starts one level deep
 *  (skipping the redundant "root" node). */
export function buildSchemaTree(schema: JsonSchemaNode | undefined): FieldNode[] {
    if (!schema) return [];
    const root = buildNode('', schema, false, 0);
    if (root.children && root.children.length > 0) return root.children;
    // Primitive body (rare) — return the root itself as a one-row tree.
    if (root.kind === 'primitive' || (!root.children && root.name === '')) {
        return [{ ...root, name: root.name || '(body)' }];
    }
    return [];
}

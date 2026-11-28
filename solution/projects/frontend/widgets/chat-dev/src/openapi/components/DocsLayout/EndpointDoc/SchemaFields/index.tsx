'use client';

import { useMemo } from 'react';

import { buildSchemaTree } from './buildTree';
import { FieldRow } from './FieldRow';

interface SchemaFieldsProps {
    schema: Record<string, unknown>;
}

/** Tree-view of a JSON schema's fields. Replaces the old flat list
 *  where nested objects appeared as ``category.id`` / ``category.name``
 *  as siblings — here they nest visually under ``category``.
 *
 *  The component is purely presentational; all shape logic lives in
 *  ``buildSchemaTree``. That split lets us swap the renderer later
 *  (e.g. virtualised rows for huge schemas) without touching the
 *  traversal. */
export function SchemaFields({ schema }: SchemaFieldsProps) {
    const tree = useMemo(() => buildSchemaTree(schema as never), [schema]);
    if (tree.length === 0) return null;

    return (
        <div className="divide-y border rounded-md overflow-hidden">
            {tree.map((node, i) => (
                <FieldRow key={`${node.name}-${i}`} field={node} depth={0} />
            ))}
        </div>
    );
}

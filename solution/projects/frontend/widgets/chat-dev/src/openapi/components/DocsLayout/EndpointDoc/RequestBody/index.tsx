'use client';

import type { ApiEndpoint } from '../../../../types';
import { SchemaFields } from '../SchemaFields';

interface RequestBodyProps {
    body: NonNullable<ApiEndpoint['requestBody']>;
}

/** Request body preview. Shows a short type summary line (``object``,
 *  ``array<object>``, …) alongside the body description, then the
 *  tree-view of fields. The example payload is rendered below in its
 *  own section (code samples) because the user often wants to copy it
 *  independently from inspecting the shape. */
export function RequestBody({ body }: RequestBodyProps) {
    const typeLabel = body.schema
        ? body.type === 'array'
            ? `array<${(body.schema as { items?: { type?: string } }).items?.type ?? 'object'}>`
            : body.type
        : body.type;

    return (
        <div className="space-y-3">
            <div className="flex items-baseline gap-2 flex-wrap">
                <code className="font-mono text-[11px] text-muted-foreground/80">{typeLabel}</code>
                {body.description && (
                    <span className="text-xs text-muted-foreground">{body.description}</span>
                )}
            </div>
            {body.schema && <SchemaFields schema={body.schema} />}
        </div>
    );
}

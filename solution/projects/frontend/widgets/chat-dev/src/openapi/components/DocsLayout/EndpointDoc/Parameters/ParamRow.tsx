'use client';

import type { ApiEndpoint } from '../../../../types';

type Param = NonNullable<ApiEndpoint['parameters']>[number];

interface ParamRowProps {
    param: Param;
}

/** Single parameter row. Name + required marker + type + (optional)
 *  description. Wrapped in ``<div>`` rather than a table row so the
 *  list degrades to a stack on narrow widths without losing semantics. */
export function ParamRow({ param }: ParamRowProps) {
    return (
        <div className="px-3 py-2.5 bg-background space-y-1">
            <div className="flex items-baseline gap-2 flex-wrap">
                <code className="font-mono text-xs font-medium text-foreground">{param.name}</code>
                {param.required && (
                    <span
                        title="Required"
                        className="text-[9px] text-destructive font-bold leading-none"
                    >
                        *
                    </span>
                )}
                <code className="font-mono text-[11px] text-muted-foreground/70">{param.type}</code>
            </div>
            {param.description && (
                <p className="text-xs text-muted-foreground leading-relaxed break-words">
                    {param.description}
                </p>
            )}
        </div>
    );
}

'use client';

import type { ApiEndpoint } from '../../../../types';
import { ParamRow } from './ParamRow';

interface ParamGroupProps {
    /** Small uppercase label shown above the group (``Path``, ``Query``). */
    label: string;
    params: NonNullable<ApiEndpoint['parameters']>;
}

/** Labelled block of parameter rows. We split path vs query so the user
 *  can tell which values go in the URL template vs the query string at
 *  a glance — both are ``parameters`` in OpenAPI terms but they land in
 *  different places in the generated request. */
export function ParamGroup({ label, params }: ParamGroupProps) {
    if (params.length === 0) return null;
    return (
        <div className="space-y-1.5">
            <div className="text-[10px] font-semibold uppercase tracking-[0.1em] text-muted-foreground/60 px-1">
                {label}
            </div>
            <div className="divide-y border rounded-md overflow-hidden">
                {params.map((p) => (
                    <ParamRow key={`${label}-${p.name}`} param={p} />
                ))}
            </div>
        </div>
    );
}

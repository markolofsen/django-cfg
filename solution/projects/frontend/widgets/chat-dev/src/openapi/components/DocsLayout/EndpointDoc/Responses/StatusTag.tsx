'use client';

import { cn } from '@djangocfg/ui-core/lib';

import { getStatusCodeStyle } from '../../../shared/http-colors';

interface StatusTagProps {
    code: string;
}

/** HTTP status pill. Colours map to the usual conventions: 2xx success,
 *  3xx info, 4xx warning, 5xx destructive, non-numeric (``default``) neutral.
 *  Codes that don't parse as integers render in the neutral style so we
 *  never flash a wrong-severity colour at the user. */
export function StatusTag({ code }: StatusTagProps) {
    const cls = getStatusCodeStyle(code);
    return (
        <span className={cn(
            'inline-flex items-center justify-center rounded border px-2 py-0.5 font-mono text-[11px] font-bold leading-none shrink-0 tabular-nums',
            cls,
        )}>
            {code}
        </span>
    );
}

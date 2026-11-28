'use client';

import { CopyButton } from '@djangocfg/ui-core/components';

import type { ApiResponse } from '../../../types';
import { StatusBadge } from '../ui';

interface StatusBarProps {
    response: ApiResponse;
    rawText: string;
    /** Content-Type label shown inline next to size/duration. ``null``
     *  when the server didn't send one — we hide the slot instead of
     *  showing an empty dash. */
    contentType: string | null;
}

/** Top strip of the response panel: status badge, statusText, size,
 *  duration, content-type, copy button. Compact — one line, tabular
 *  numerals so 1.4 KB and 107ms don't shift as values update. */
export function StatusBar({ response, rawText, contentType }: StatusBarProps) {
    const sizeKb = rawText ? `${(rawText.length / 1024).toFixed(1)} KB` : '';
    const duration = response.duration != null ? `${response.duration}ms` : '';
    const hasStatus = response.status != null;
    const hasCopy = Boolean(rawText);

    return (
        <div className="shrink-0 border-b px-4 py-2 flex items-center justify-between gap-3 bg-muted/20">
            <div className="flex items-center gap-2 min-w-0">
                {hasStatus && <StatusBadge status={response.status!} />}
                {response.statusText && (
                    <span className="text-xs text-muted-foreground truncate">
                        {response.statusText}
                    </span>
                )}
                {sizeKb && (
                    <span className="text-[10px] text-muted-foreground/50 tabular-nums shrink-0">
                        {sizeKb}
                    </span>
                )}
                {duration && (
                    <span className="text-[10px] text-muted-foreground/50 tabular-nums shrink-0">
                        {duration}
                    </span>
                )}
                {contentType && (
                    <span className="text-[10px] text-muted-foreground/50 font-mono truncate">
                        {contentType}
                    </span>
                )}
            </div>
            {hasCopy && (
                <CopyButton
                    value={rawText}
                    variant="ghost"
                    size="sm"
                    className="h-6 px-2 text-[10px] text-muted-foreground shrink-0"
                >
                    Copy
                </CopyButton>
            )}
        </div>
    );
}

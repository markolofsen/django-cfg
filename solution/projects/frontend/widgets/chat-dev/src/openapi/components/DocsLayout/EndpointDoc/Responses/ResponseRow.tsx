'use client';

import { ChevronRight } from 'lucide-react';
import { useState } from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import type { ApiEndpoint } from '../../../../types';
import { ResponseBody } from './ResponseBody';
import { StatusTag } from './StatusTag';

interface ResponseRowProps {
    response: NonNullable<ApiEndpoint['responses']>[number];
}

/** One status-code row in the Responses section.
 *
 *  Layout:
 *    - Chevron column only renders when there's an example to expand.
 *      Otherwise the row is inert (no button wrapper, no hover state)
 *      and the space stays tight instead of reserving an empty gutter
 *      under a disabled chevron.
 *    - Status tag column is ``48px`` wide — enough for ``default`` and
 *      3-digit codes in the font size we use. Keeps descriptions
 *      aligned on their left edge across all rows regardless of code.
 *
 *  Expansion defaults:
 *    - 2xx with example → open (happy-path is what readers want first).
 *    - Everything else → closed, one click to inspect. */
export function ResponseRow({ response }: ResponseRowProps) {
    const hasExample = Boolean(response.example);
    const numeric = Number.parseInt(response.code, 10);
    const isSuccess = Number.isFinite(numeric) && numeric >= 200 && numeric < 300;
    const [open, setOpen] = useState(hasExample && isSuccess);

    // Inert row (no example available) — render as a plain div so the
    // layout stays identical but without button affordances.
    if (!hasExample) {
        return (
            <div className="flex items-center gap-3 px-3 py-2 bg-background">
                <div className="w-12 shrink-0 flex justify-start">
                    <StatusTag code={response.code} />
                </div>
                <span className="text-sm text-muted-foreground leading-relaxed break-words min-w-0">
                    {response.description}
                </span>
            </div>
        );
    }

    return (
        <div className="bg-background">
            <button
                type="button"
                onClick={() => setOpen((v) => !v)}
                className="w-full flex items-center gap-3 px-3 py-2 text-left hover:bg-muted/40 cursor-pointer transition-colors"
                aria-expanded={open}
            >
                <ChevronRight
                    className={cn(
                        'h-3.5 w-3.5 text-muted-foreground/60 transition-transform shrink-0',
                        open && 'rotate-90',
                    )}
                />
                <div className="w-12 shrink-0 flex justify-start">
                    <StatusTag code={response.code} />
                </div>
                <span className="text-sm text-muted-foreground leading-relaxed break-words min-w-0 flex-1">
                    {response.description}
                </span>
            </button>
            {open && (
                <ResponseBody
                    example={response.example!}
                    contentType={response.contentType}
                />
            )}
        </div>
    );
}

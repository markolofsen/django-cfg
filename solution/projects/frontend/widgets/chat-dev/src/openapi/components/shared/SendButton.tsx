'use client';

import { AlertCircle, Loader2, Send } from 'lucide-react';
import React, { useMemo } from 'react';

import { Button } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { usePlaygroundContext } from '../../context/PlaygroundContext';
import { isValidJson } from '../../utils';
import { UrlBuilder } from '../../utils/url';

interface SendButtonProps {
    className?: string;
}

/**
 * Standalone Send button that reads from and acts on the playground
 * context. Disabled + explainer-banner when required inputs are missing.
 *
 * Validation rules (in order — first failure wins the banner text):
 *   1. Required path/query parameters must be non-empty.
 *   2. Path template must be fully substituted (no leftover ``{name}``).
 *   3. Request body, when present, must be valid JSON.
 *
 * We validate on the client so the user isn't punished with a 404 from
 * the server for a trivially detectable mistake (e.g. empty ``{petId}``).
 */
export function SendButton({ className }: SendButtonProps) {
    const { state, sendRequest } = usePlaygroundContext();

    const ep = state.selectedEndpoint;

    // Single source of truth for URL-level validation lives in UrlBuilder.
    // Recomputing every render is cheap (pure string work).
    const builder = useMemo(
        () => (ep ? new UrlBuilder(ep, state.parameters) : null),
        [ep, state.parameters],
    );
    const missingRequired = builder?.missingRequired() ?? [];
    const unsubstituted = builder?.unfilledPlaceholders() ?? [];

    const isJsonValid = state.requestBody ? isValidJson(state.requestBody) : true;

    const blockers: string[] = [];
    if (missingRequired.length > 0) {
        blockers.push(
            `Fill required parameter${missingRequired.length > 1 ? 's' : ''}: ${missingRequired.join(', ')}`,
        );
    } else if (unsubstituted.length > 0) {
        blockers.push(`URL still has unfilled placeholder${unsubstituted.length > 1 ? 's' : ''}: ${unsubstituted.map((n) => `{${n}}`).join(', ')}`);
    }
    if (!isJsonValid) blockers.push('Request body is not valid JSON');

    const disabled =
        state.loading ||
        !state.requestUrl ||
        blockers.length > 0;

    const tooltip = blockers.length > 0 ? blockers.join('\n') : undefined;

    return (
        <div className={cn('space-y-2', className)}>
            {blockers.length > 0 && (
                <div className="flex items-start gap-2 rounded-md border border-warning-border bg-warning-background px-3 py-2 text-[11px] text-warning-foreground">
                    <AlertCircle className="h-3.5 w-3.5 shrink-0 mt-px" />
                    <span className="leading-snug">{blockers[0]}</span>
                </div>
            )}
            <Button
                onClick={sendRequest}
                disabled={disabled}
                size="sm"
                title={tooltip}
                className="w-full gap-2 h-9"
            >
                {state.loading ? (
                    <>
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                        Sending…
                    </>
                ) : (
                    <>
                        <Send className="h-3.5 w-3.5" />
                        Send Request
                    </>
                )}
            </Button>
        </div>
    );
}

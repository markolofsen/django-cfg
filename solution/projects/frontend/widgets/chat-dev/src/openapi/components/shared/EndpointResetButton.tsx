'use client';

import { RotateCcw } from 'lucide-react';
import React, { useCallback } from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import { usePlaygroundContext } from '../../context/PlaygroundContext';
import { useEndpointDraft } from '../../hooks/useEndpointDraft';

/**
 * "Reset" ghost button for the current endpoint's draft.
 *
 * Wipes both the in-memory context state (parameters + body) and the
 * persisted localStorage entry. We call reset() *after* clearing the
 * context so the EndpointDraftSync effect that mirrors state → storage
 * doesn't immediately re-create a now-empty draft with an empty object
 * (benign, but uglier in storage).
 */
export function EndpointResetButton() {
    const { state, setParameters, setRequestBody } = usePlaygroundContext();
    const ep = state.selectedEndpoint;
    const { reset } = useEndpointDraft(state.activeSchemaId, ep);

    const hasDraft =
        Object.keys(state.parameters).length > 0 || state.requestBody.length > 0;

    const onClick = useCallback(() => {
        setParameters({});
        setRequestBody('');
        reset();
    }, [setParameters, setRequestBody, reset]);

    if (!ep || !hasDraft) return null;

    return (
        <button
            type="button"
            onClick={onClick}
            title="Reset parameters & body (keeps auth)"
            className={cn(
                'inline-flex items-center gap-1 text-[10px] text-muted-foreground',
                'hover:text-foreground transition-colors',
            )}
        >
            <RotateCcw className="h-2.5 w-2.5" />
            Reset
        </button>
    );
}

'use client';

import { useEffect, useRef } from 'react';

import { usePlaygroundContext } from '../../context/PlaygroundContext';
import { useEndpointDraft } from '../../hooks/useEndpointDraft';

interface EndpointDraftSyncProps {
    /** Active schema id (so drafts don't bleed between different APIs).
     *  When null — drafts are disabled (hook returns empty draft, writes
     *  are no-ops). Pass the current schema's ``id`` from useOpenApiSchema. */
    schemaId: string | null;
}

/**
 * Headless component: keeps ``RequestPanel`` state mirrored with a
 * per-endpoint draft in localStorage.
 *
 * Flow:
 *   1. On endpoint change ⇒ read draft ⇒ push into context state.
 *   2. On context state change (user edits params/body) ⇒ write draft.
 *
 * Step 1 is gated by a ref so "just-loaded" drafts don't immediately
 * trigger step 2. Step 2 additionally compares against a serialised
 * snapshot of the last persisted value so a re-render without a real
 * value change doesn't touch storage.
 *
 * Had an infinite-render-loop bug here earlier: the persist callbacks
 * were driven by ``useLocalStorage`` whose setter identity changed on
 * every internal state update, so depending on them from an effect
 * created a cycle. Fixed by making ``useEndpointDraft``'s writers
 * stable (ref-based), and by gating writes with value comparison below.
 */
export function EndpointDraftSync({ schemaId }: EndpointDraftSyncProps) {
    const { state, setParameters, setRequestBody, setActiveSchemaId } = usePlaygroundContext();
    const ep = state.selectedEndpoint;

    // Mirror schemaId into context so other components (e.g. the Reset
    // button in RequestPanel) can read it without receiving props from
    // a parent they don't own.
    useEffect(() => {
        setActiveSchemaId(schemaId);
    }, [schemaId, setActiveSchemaId]);

    const { draft, setParameters: persistParams, setRequestBody: persistBody } =
        useEndpointDraft(schemaId, ep);

    const lastLoadedKeyRef = useRef<string | null>(null);
    const lastPersistedParamsRef = useRef<string>('');
    const lastPersistedBodyRef = useRef<string>('');
    const currentKey = ep ? `${ep.method}|${ep.path}` : null;

    // Step 1 — hydrate context from draft on endpoint switch.
    //
    // IMPORTANT: only apply fields that actually exist in the saved draft.
    // SELECT_ENDPOINT in the reducer pre-fills ``requestBody`` with an
    // auto-generated schema example, and ``parameters`` with ``{}``.
    // If we blindly overwrite those with an empty draft we wipe the
    // example before the user ever sees it. Tracked via a bug: opening
    // POST /pet showed ``{"key":"value"}`` instead of the Pet example.
    useEffect(() => {
        if (!ep || !currentKey) {
            lastLoadedKeyRef.current = null;
            return;
        }
        if (lastLoadedKeyRef.current === currentKey) return;
        lastLoadedKeyRef.current = currentKey;

        const hasStoredParams =
            draft.parameters && Object.keys(draft.parameters).length > 0;
        const hasStoredBody = typeof draft.requestBody === 'string' && draft.requestBody !== '';

        if (hasStoredParams) {
            setParameters(draft.parameters);
            lastPersistedParamsRef.current = JSON.stringify(draft.parameters);
        } else {
            // Keep whatever the reducer put there; mirror it into the
            // "last persisted" ref so step-2 treats it as a baseline.
            lastPersistedParamsRef.current = JSON.stringify(state.parameters);
        }

        if (hasStoredBody) {
            setRequestBody(draft.requestBody);
            lastPersistedBodyRef.current = draft.requestBody;
        } else {
            lastPersistedBodyRef.current = state.requestBody;
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [currentKey]);

    // Step 2 — persist user edits.
    useEffect(() => {
        if (!ep || lastLoadedKeyRef.current !== currentKey) return;
        const serialised = JSON.stringify(state.parameters);
        if (serialised === lastPersistedParamsRef.current) return;
        lastPersistedParamsRef.current = serialised;
        persistParams(state.parameters);
    }, [state.parameters, ep, currentKey, persistParams]);

    useEffect(() => {
        if (!ep || lastLoadedKeyRef.current !== currentKey) return;
        if (state.requestBody === lastPersistedBodyRef.current) return;
        lastPersistedBodyRef.current = state.requestBody;
        persistBody(state.requestBody);
    }, [state.requestBody, ep, currentKey, persistBody]);

    return null;
}

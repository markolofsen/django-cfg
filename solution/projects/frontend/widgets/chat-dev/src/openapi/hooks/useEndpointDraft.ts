'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

import type { ApiEndpoint } from '../types';
import { CFG_FAMILIES, cfgStorage } from '@djangocfg/api/storage';

/**
 * Per-endpoint draft kept in localStorage so user input survives across
 * reloads and across switching back-and-forth between endpoints.
 *
 * Scoped by ``schemaId`` + ``method`` + ``path`` — two endpoints on the
 * same path with different methods don't share drafts. Two different
 * APIs don't collide either.
 *
 * Storage shape:
 *   { parameters: { [name]: string }, requestBody: string }
 *
 * Implementation note: we deliberately DO NOT build on top of
 * ``useLocalStorage`` here. That hook's ``setValue`` callback reference
 * changes whenever its internal state changes, and when EndpointDraftSync
 * mirrors context → draft, the chain
 *   state change ⇒ persist call ⇒ hook state change ⇒ new callback ⇒
 *   effect rerun ⇒ persist call …
 * blew up into a maximum-update-depth loop. Writing straight to
 * ``localStorage`` with a stable ref-based writer breaks the cycle.
 */
export interface EndpointDraft {
    parameters: Record<string, string>;
    requestBody: string;
}

const EMPTY_DRAFT: EndpointDraft = { parameters: {}, requestBody: '' };

function storageKey(schemaId: string | null, ep: ApiEndpoint | null): string | null {
    if (!schemaId || !ep) return null;
    return cfgStorage.familyKey(CFG_FAMILIES.agentEndpointDraft, `${schemaId}_${ep.method}_${ep.path}`);
}

function readDraft(key: string | null): EndpointDraft {
    if (!key || typeof window === 'undefined') return EMPTY_DRAFT;
    try {
        const raw = window.localStorage.getItem(key);
        if (!raw) return EMPTY_DRAFT;
        const parsed = JSON.parse(raw) as Partial<EndpointDraft>;
        return {
            parameters: parsed?.parameters ?? {},
            requestBody: typeof parsed?.requestBody === 'string' ? parsed.requestBody : '',
        };
    } catch {
        return EMPTY_DRAFT;
    }
}

function writeDraft(key: string | null, value: EndpointDraft): void {
    if (!key || typeof window === 'undefined') return;
    try {
        // Skip writes for empty drafts — reduces storage noise and keeps
        // "never edited" endpoints out of storage entirely.
        if (Object.keys(value.parameters).length === 0 && !value.requestBody) {
            window.localStorage.removeItem(key);
            return;
        }
        window.localStorage.setItem(key, JSON.stringify(value));
    } catch {
        // Quota / private mode — silently drop; UI state still works.
    }
}

export interface UseEndpointDraftResult {
    /** Draft snapshot loaded on mount / endpoint change. Does not update
     *  as the user types — the caller owns the "live" state (context). */
    draft: EndpointDraft;
    /** Persist the current parameters. Safe to call on every change;
     *  writes skip when the endpoint has no key yet. */
    setParameters: (params: Record<string, string>) => void;
    setRequestBody: (body: string) => void;
    /** Wipe the persisted draft for the current endpoint. */
    reset: () => void;
}

export function useEndpointDraft(
    schemaId: string | null,
    endpoint: ApiEndpoint | null,
): UseEndpointDraftResult {
    const key = storageKey(schemaId, endpoint);

    // ``draft`` is reloaded from storage only when the key changes —
    // not when we write. Writes don't need to come back to us because
    // the caller keeps the live state and re-reads on key change.
    const [draft, setDraftSnapshot] = useState<EndpointDraft>(() => readDraft(key));

    // Track the last loaded key so we reload exactly once per endpoint.
    const loadedKeyRef = useRef<string | null>(key);
    useEffect(() => {
        if (loadedKeyRef.current === key) return;
        loadedKeyRef.current = key;
        setDraftSnapshot(readDraft(key));
    }, [key]);

    // Keep a ref of the current key so the writers below stay stable
    // across renders — React callback identity was the root cause of
    // the infinite render loop we had before.
    const keyRef = useRef(key);
    useEffect(() => {
        keyRef.current = key;
    }, [key]);

    // Same for the latest full draft value — both writers need to merge
    // their field into the last known shape before writing.
    const latestRef = useRef<EndpointDraft>(draft);
    useEffect(() => {
        latestRef.current = draft;
    }, [draft]);

    const setParameters = useCallback((params: Record<string, string>) => {
        const next: EndpointDraft = {
            parameters: params,
            requestBody: latestRef.current.requestBody,
        };
        latestRef.current = next;
        writeDraft(keyRef.current, next);
    }, []);

    const setRequestBody = useCallback((body: string) => {
        const next: EndpointDraft = {
            parameters: latestRef.current.parameters,
            requestBody: body,
        };
        latestRef.current = next;
        writeDraft(keyRef.current, next);
    }, []);

    const reset = useCallback(() => {
        latestRef.current = EMPTY_DRAFT;
        if (keyRef.current && typeof window !== 'undefined') {
            try { window.localStorage.removeItem(keyRef.current); } catch { /* noop */ }
        }
        setDraftSnapshot(EMPTY_DRAFT);
    }, []);

    return { draft, setParameters, setRequestBody, reset };
}

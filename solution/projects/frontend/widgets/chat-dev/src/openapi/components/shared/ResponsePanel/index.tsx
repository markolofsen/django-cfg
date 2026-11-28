'use client';

import { Loader2, Send, Terminal, WifiOff } from 'lucide-react';
import { useEffect, useState } from 'react';

import { usePlaygroundContext } from '../../../context/PlaygroundContext';
import { EmptyState, ScrollArea } from '../ui';
import { PreviewView } from './PreviewView';
import { PrettyView } from './PrettyView';
import { RawView } from './RawView';
import { StatusBar } from './StatusBar';
import type { ViewMode } from './types';
import { useResponseView } from './useResponseView';
import { ViewTabs } from './ViewTabs';

/** Response panel used by both the sticky ``SlideInPlayground`` and the
 *  modal ``TryItSheet``. Responsibilities:
 *    - Empty / loading / network-error gates
 *    - Three view modes (Pretty / Raw / Preview) with a tab bar
 *    - Auto-pick the best default view per response type (JSON → Pretty,
 *      HTML → Preview, everything else → Pretty as the widest-purpose)
 *
 *  View mode is local component state rather than context state — it
 *  should reset when the selected endpoint changes and not leak between
 *  endpoints. */
export function ResponsePanel() {
    const { state } = usePlaygroundContext();
    const { response, loading, selectedEndpoint } = state;

    const { treeData, rawText, detected } = useResponseView(response?.data, response?.headers);
    const showPreview = detected.kind === 'html';

    // Default view heuristic: show HTML pages preview-first so the
    // reader sees the actual rendered server page immediately.
    // Everything else lands on Pretty.
    const [mode, setMode] = useState<ViewMode>(showPreview ? 'preview' : 'pretty');

    // Reset the mode when the endpoint or response changes so a
    // previously-selected tab from a different shape doesn't stick
    // around (e.g. stuck on Preview when switching from HTML→JSON).
    useEffect(() => {
        setMode(showPreview ? 'preview' : 'pretty');
    }, [selectedEndpoint, response, showPreview]);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full gap-2">
                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                <span className="text-xs text-muted-foreground">Sending…</span>
            </div>
        );
    }

    if (!selectedEndpoint) return <EmptyState icon={Terminal} text="Response will appear here" />;
    if (!response)         return <EmptyState icon={Send} text='Press "Send Request" to see the response' />;

    const hasError = Boolean(response.error);
    const hasStatus = response.status != null;

    // Pure network error (no HTTP response at all — CORS, offline, timeout)
    if (hasError && !hasStatus) {
        return (
            <EmptyState
                icon={WifiOff}
                text={response.error!}
                className="text-destructive [&_svg]:text-destructive"
            />
        );
    }

    return (
        <>
            <StatusBar response={response} rawText={rawText} contentType={detected.contentType} />

            {/* HTTP-level error body (4xx/5xx — has status but also error flag) */}
            {hasError && (
                <div className="shrink-0 mx-4 mt-3 rounded border border-destructive/20 bg-destructive/5 px-3 py-2">
                    <p className="text-xs text-destructive">{response.error}</p>
                </div>
            )}

            <ViewTabs active={mode} onChange={setMode} showPreview={showPreview} />

            <ScrollArea>
                {mode === 'pretty' && (
                    <PrettyView treeData={treeData} rawText={rawText} detected={detected} />
                )}
                {mode === 'raw' && <RawView rawText={rawText} />}
                {mode === 'preview' && <PreviewView html={rawText} />}
            </ScrollArea>
        </>
    );
}

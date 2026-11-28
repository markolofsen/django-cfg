'use client';

import React from 'react';

import { SidePanel } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { usePlaygroundContext } from '../../context/PlaygroundContext';
import { RequestPanel } from '../shared/RequestPanel';
import { ResponsePanel } from '../shared/ResponsePanel';
import { SendButton } from '../shared/SendButton';
import { MethodBadge, Panel, relativePath } from '../shared/ui';

interface SlideInPlaygroundProps {
    open: boolean;
    onClose: () => void;
}

// Width when only Request is visible vs. when Response is also rendered.
// ``clamp(min, preferred, max)`` lets the panel scale with the viewport
// instead of sitting at a fixed size that looks tiny on ultra-wide or
// cramped on laptops.
//
// Narrow (Request only) — form content, no need to ever exceed ~480px.
//   1280 viewport → 384  | 1440 → 432 | 1920 → 480 (cap) | 2560 → 480 (cap)
//
// Wide (Request + Response) — response can be huge JSON/HTML; give it room.
//   1280 → 768 | 1440 → 864 | 1920 → 1152 | 2560 → 1280 (cap) | 3840 → 1280 (cap)
//
// Transition between the two values is animated by SidePanel.Content
// (both ``transform`` and ``width`` listed there). clamp() interpolates
// smoothly during that transition, no extra plumbing needed.
const WIDTH_NARROW = 'clamp(380px, 30vw, 480px)';
const WIDTH_WIDE = 'clamp(720px, 60vw, 1280px)';

/**
 * Right-side slide-in playground. Two-column layout appears once the
 * user has a response in hand — before that, only the Request form is
 * shown and the panel stays narrow so docs have room to breathe.
 *
 * State transitions:
 *   - no endpoint        ⇒ panel not rendered
 *   - endpoint, no resp  ⇒ narrow (Request only)
 *   - endpoint + loading ⇒ wide (Request + Response spinner)
 *   - endpoint + resp    ⇒ wide (Request + Response)
 *
 * Selecting a different endpoint clears ``response`` in the reducer,
 * so the panel smoothly collapses back to narrow.
 */
export function SlideInPlayground({ open, onClose }: SlideInPlaygroundProps) {
    const { state } = usePlaygroundContext();
    const ep = state.selectedEndpoint;
    const showResponse = state.response !== null || state.loading;
    const width = showResponse ? WIDTH_WIDE : WIDTH_NARROW;

    return (
        <SidePanel open={open} onOpenChange={(v) => !v && onClose()} side="right">
            <SidePanel.Content width={width} className="max-w-[95vw]">
                <SidePanel.Header>
                    <SidePanel.Title>Playground</SidePanel.Title>
                    {ep && (
                        <div className="flex items-center gap-2 min-w-0 flex-1">
                            <MethodBadge method={ep.method} />
                            <code className="font-mono text-[11px] text-muted-foreground truncate">
                                {relativePath(ep.path)}
                            </code>
                        </div>
                    )}
                    <SidePanel.Close className="ml-auto" />
                </SidePanel.Header>

                {/* Body: 1 or 2 columns depending on whether we have a
                    response to show. ``divide-x`` gives a 1px seam
                    between the panes so they read as distinct surfaces.
                    Send button lives inside the Request column so it
                    reads as an action on the form it belongs to — not
                    as a page-level footer that ambiguously sat under
                    the response column too. */}
                <SidePanel.Body
                    className={cn(
                        'overflow-hidden grid divide-x transition-[grid-template-columns] duration-250',
                        showResponse
                            ? 'grid-cols-[minmax(0,1fr)_minmax(0,1fr)]'
                            : 'grid-cols-1',
                    )}
                >
                    <Panel>
                        <RequestPanel />
                        {ep && (
                            <div className="shrink-0 border-t px-4 py-3 bg-background">
                                <SendButton />
                            </div>
                        )}
                    </Panel>
                    {showResponse && (
                        <Panel>
                            <ResponsePanel />
                        </Panel>
                    )}
                </SidePanel.Body>
            </SidePanel.Content>
        </SidePanel>
    );
}

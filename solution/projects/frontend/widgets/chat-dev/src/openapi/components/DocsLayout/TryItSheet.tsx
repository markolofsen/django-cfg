'use client';

import React from 'react';

import {
    ResponsiveSheet,
    ResponsiveSheetContent,
    ResponsiveSheetHeader,
    ResponsiveSheetTitle,
} from '@djangocfg/ui-core/components';

import { usePlaygroundContext } from '../../context/PlaygroundContext';
import { RequestPanel } from '../shared/RequestPanel';
import { ResponsePanel } from '../shared/ResponsePanel';
import { SendButton } from '../shared/SendButton';

interface TryItSheetProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

/**
 * Mobile/tablet fallback: the slide-in playground doesn't fit, so we
 * open Request + Response inside a ResponsiveSheet (bottom drawer on
 * mobile, side sheet on desktop). Response stays hidden until a
 * request has been sent — matching the desktop ``SlideInPlayground``
 * behaviour.
 */
export function TryItSheet({ open, onOpenChange }: TryItSheetProps) {
    const { state } = usePlaygroundContext();
    const showResponse = state.response !== null || state.loading;

    return (
        <ResponsiveSheet open={open} onOpenChange={onOpenChange}>
            <ResponsiveSheetContent className="sm:max-w-xl flex flex-col h-full p-0">
                <ResponsiveSheetHeader className="px-4 py-3 border-b shrink-0">
                    <ResponsiveSheetTitle className="text-sm">Playground</ResponsiveSheetTitle>
                </ResponsiveSheetHeader>
                {/* Send button sits inside the Request section so it
                    reads as an action on the form, not an ambiguous
                    page-level footer when Response is also visible. */}
                <div className="flex-1 min-h-0 flex flex-col divide-y">
                    <div className="flex-1 min-h-0 flex flex-col">
                        <RequestPanel />
                        {state.selectedEndpoint && (
                            <div className="shrink-0 border-t px-4 py-3 bg-background">
                                <SendButton />
                            </div>
                        )}
                    </div>
                    {showResponse && (
                        <div className="flex-1 min-h-0 flex flex-col">
                            <ResponsePanel />
                        </div>
                    )}
                </div>
            </ResponsiveSheetContent>
        </ResponsiveSheet>
    );
}

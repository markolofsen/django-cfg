'use client';

import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface MermaidErrorPanelProps {
    /** Human-readable error message from the Mermaid parser. */
    message: string;
}

/**
 * Inline error panel shown when a Mermaid diagram fails to parse.
 *
 * Replaces the previous `innerHTML`-injected markup — keeps rendering in
 * React, uses semantic `destructive` tokens, and stays accessible
 * (`role="alert"`).
 */
export const MermaidErrorPanel: React.FC<MermaidErrorPanelProps> = ({ message }) => {
    return (
        <div
            role="alert"
            className="flex items-start gap-3 rounded-md border border-destructive/30 bg-destructive/10 p-4 text-destructive"
        >
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
            <div className="min-w-0">
                <p className="text-sm font-semibold">Diagram syntax error</p>
                <p className="mt-0.5 break-words text-sm text-destructive/90">{message}</p>
            </div>
        </div>
    );
};

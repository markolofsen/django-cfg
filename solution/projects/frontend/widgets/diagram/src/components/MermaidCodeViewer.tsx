'use client';

import React, { useEffect, useRef, useState } from 'react';

interface MermaidCodeViewerProps {
    chart: string;
    renderPreview: () => React.ReactNode;
}

export const MermaidCodeViewer: React.FC<MermaidCodeViewerProps> = ({
    chart,
    renderPreview,
}) => {
    const [activeTab, setActiveTab] = useState<'preview' | 'code'>('preview');
    const [copied, setCopied] = useState(false);
    // One timer, cleared on unmount: closing the viewer within the confirm
    // window left a scheduled setState behind, and copying twice stacked two.
    const copiedTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    useEffect(
        () => () => {
            if (copiedTimerRef.current) clearTimeout(copiedTimerRef.current);
        },
        [],
    );

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(chart);
        } catch {
            // Denied permission or an insecure origin — no tick to show.
            return;
        }
        setCopied(true);
        if (copiedTimerRef.current) clearTimeout(copiedTimerRef.current);
        copiedTimerRef.current = setTimeout(() => {
            copiedTimerRef.current = null;
            setCopied(false);
        }, 2000);
    };

    return (
        <div className="flex flex-col h-full">
            {/* Tabs */}
            <div className="flex items-center justify-between border-b border-border px-4">
                <div className="flex">
                    <button
                        onClick={() => setActiveTab('preview')}
                        className={`px-4 py-3 text-sm font-medium transition-colors relative ${
                            activeTab === 'preview'
                                ? 'text-foreground'
                                : 'text-muted-foreground hover:text-foreground'
                        }`}
                    >
                        Preview
                        {activeTab === 'preview' && (
                            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
                        )}
                    </button>
                    <button
                        onClick={() => setActiveTab('code')}
                        className={`px-4 py-3 text-sm font-medium transition-colors relative ${
                            activeTab === 'code'
                                ? 'text-foreground'
                                : 'text-muted-foreground hover:text-foreground'
                        }`}
                    >
                        Code
                        {activeTab === 'code' && (
                            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
                        )}
                    </button>
                </div>

                {/* Copy button - show only on Code tab */}
                {activeTab === 'code' && (
                    <button
                        onClick={handleCopy}
                        className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-primary/10 hover:bg-primary/20 text-primary rounded transition-colors"
                    >
                        {copied ? (
                            <>
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                </svg>
                                Copied!
                            </>
                        ) : (
                            <>
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                </svg>
                                Copy
                            </>
                        )}
                    </button>
                )}
            </div>

            {/* Content */}
            <div className="flex-1 overflow-auto">
                {activeTab === 'preview' ? (
                    <div className="p-6 flex items-center justify-center min-h-full">
                        {renderPreview()}
                    </div>
                ) : (
                    <pre className="p-6 text-sm font-mono text-foreground bg-muted/30 h-full overflow-auto">
                        <code>{chart}</code>
                    </pre>
                )}
            </div>
        </div>
    );
};

'use client';

import { cn } from '@djangocfg/ui-core/lib';

import type { ViewMode } from './types';

interface ViewTabsProps {
    active: ViewMode;
    onChange: (mode: ViewMode) => void;
    /** When false the Preview tab is hidden — only HTML responses get
     *  a useful preview, everything else renders the same as Pretty. */
    showPreview: boolean;
}

const LABELS: Record<ViewMode, string> = {
    pretty: 'Pretty',
    raw: 'Raw',
    preview: 'Preview',
};

/** Tab strip for switching between Pretty / Raw / Preview. Matches the
 *  visual weight of the ``LanguageTabs`` in CodeSamples so the page
 *  reads as one coherent toolbar system. */
export function ViewTabs({ active, onChange, showPreview }: ViewTabsProps) {
    const tabs: ViewMode[] = showPreview ? ['pretty', 'raw', 'preview'] : ['pretty', 'raw'];
    return (
        <div className="shrink-0 border-b px-3 py-1.5 flex items-center gap-1">
            {tabs.map((t) => (
                <button
                    key={t}
                    type="button"
                    onClick={() => onChange(t)}
                    className={cn(
                        'h-6 px-2.5 rounded text-[11px] font-medium transition-colors',
                        active === t
                            ? 'bg-muted text-foreground'
                            : 'text-muted-foreground/70 hover:text-foreground hover:bg-muted/50',
                    )}
                >
                    {LABELS[t]}
                </button>
            ))}
        </div>
    );
}

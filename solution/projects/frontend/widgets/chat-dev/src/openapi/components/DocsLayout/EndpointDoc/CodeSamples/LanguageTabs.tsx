'use client';

import { cn } from '@djangocfg/ui-core/lib';

import { CODE_SAMPLE_TARGETS, type CodeSampleTargetId } from '../../../../utils/codeSamples';

interface LanguageTabsProps {
    activeId: CodeSampleTargetId;
    onChange: (id: CodeSampleTargetId) => void;
}

/** Horizontal tab strip for switching between cURL/JS/Python/… The
 *  strip scrolls horizontally on narrow viewports rather than wrapping
 *  to a second line so the adjacent code block keeps its vertical
 *  rhythm. */
export function LanguageTabs({ activeId, onChange }: LanguageTabsProps) {
    return (
        <div className="flex items-center gap-1 overflow-x-auto -mx-1 px-1">
            {CODE_SAMPLE_TARGETS.map((t) => (
                <button
                    key={t.id}
                    type="button"
                    onClick={() => onChange(t.id)}
                    className={cn(
                        'shrink-0 h-7 px-2.5 rounded text-xs font-medium transition-colors',
                        activeId === t.id
                            ? 'bg-muted text-foreground'
                            : 'text-muted-foreground/70 hover:text-foreground hover:bg-muted/50',
                    )}
                >
                    {t.label}
                </button>
            ))}
        </div>
    );
}

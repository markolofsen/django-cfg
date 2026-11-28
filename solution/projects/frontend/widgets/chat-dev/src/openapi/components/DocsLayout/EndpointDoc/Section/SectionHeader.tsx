'use client';

import { Check, ChevronDown, Link2 } from 'lucide-react';
import { useState } from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import { useEndpointDocContext } from '../context';
import { buildSectionHash } from '../hooks/useSectionHash';
import type { SectionId } from '../types';

interface SectionHeaderProps {
    /** Section identifier — needed to build the shareable hash link. */
    sectionId: SectionId;
    title: string;
    badge?: number;
    open: boolean;
    onToggle: () => void;
}

/** Clickable header for a collapsible section. The whole row toggles,
 *  plus a hover-revealed anchor button copies a ``#section=...`` URL so
 *  users can share a link that lands with this exact section already
 *  expanded (handled by ``useSectionHashRouter``). */
export function SectionHeader({ sectionId, title, badge, open, onToggle }: SectionHeaderProps) {
    const { endpointId } = useEndpointDocContext();
    const [copied, setCopied] = useState(false);

    const copyHash = (e: React.MouseEvent) => {
        // Prevent the row toggle — the anchor button must not collapse
        // the section while the user is copying the link.
        e.stopPropagation();
        if (typeof window === 'undefined') return;
        const hash = buildSectionHash(endpointId, sectionId);
        const url = `${window.location.origin}${window.location.pathname}#${hash}`;
        void navigator.clipboard?.writeText(url).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 1200);
        });
    };

    return (
        <div
            className={cn(
                'group/section w-full flex items-center gap-2 py-1.5 -ml-1 px-1 rounded cursor-pointer',
                'hover:bg-muted/30 transition-colors',
            )}
            onClick={onToggle}
            role="button"
            aria-expanded={open}
            tabIndex={0}
            onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    onToggle();
                }
            }}
        >
            <ChevronDown
                className={cn(
                    'h-3.5 w-3.5 text-muted-foreground/50 transition-transform shrink-0',
                    !open && '-rotate-90',
                )}
            />
            <h4 className="text-[10px] font-semibold uppercase tracking-[0.12em] text-muted-foreground/80">
                {title}
            </h4>
            {typeof badge === 'number' && badge > 0 && (
                <span className="font-mono text-[10px] text-muted-foreground/50 tabular-nums">
                    {badge}
                </span>
            )}
            <button
                type="button"
                onClick={copyHash}
                title="Copy link to this section"
                className={cn(
                    'ml-auto shrink-0 p-1 rounded text-muted-foreground/40 hover:text-foreground hover:bg-muted transition-all',
                    'opacity-0 group-hover/section:opacity-100 focus-visible:opacity-100',
                    copied && 'opacity-100 text-success',
                )}
            >
                {copied ? <Check className="h-3 w-3" /> : <Link2 className="h-3 w-3" />}
            </button>
        </div>
    );
}

'use client';

import {
    Check,
    ChevronsDownUp,
    ChevronsUpDown,
    Link2,
} from 'lucide-react';
import React, { useCallback, useMemo, useState } from 'react';

import {
    TooltipHint,
} from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { useEndpointDocContext } from '../context';
import { sectionKey, useEndpointDocStore } from '../store';
import type { SectionId } from '../types';

interface MetaActionsProps {
    anchor: string;
    /** Sections present on this endpoint — expand/collapse acts only
     *  on visible rows, never on catalogue items the card doesn't render. */
    presentSections: readonly SectionId[];
}

interface IconButtonProps {
    label: string;
    onClick: () => void;
    children: React.ReactNode;
    active?: boolean;
}

/** Tight 24×24 icon button used across the meta row. Keeps the hit
 *  target compact so the row reads as a secondary metadata strip, not
 *  a toolbar that competes with the path for attention. */
function IconButton({ label, onClick, children, active }: IconButtonProps) {
    return (
        <TooltipHint tooltip={{ content: <span className="text-[11px]">{label}</span>, side: 'bottom' }}>
          <button
              type="button"
              onClick={onClick}
              aria-label={label}
              className={cn(
                  'shrink-0 h-6 w-6 inline-flex items-center justify-center rounded',
                  'text-muted-foreground/60 hover:text-foreground hover:bg-muted transition-colors',
                  active && 'text-success hover:text-success',
              )}
          >
              {children}
          </button>
        </TooltipHint>
    );
}

/** Inline meta-row actions: copy link · expand/collapse all. Actions
 *  are always visible (corporate tool pattern) but sized down so the
 *  path on the next line stays the visual focal point. The
 *  AI-friendly "AI Copy" used to live here as another icon — it was
 *  invisible at that size, so it now sits next to "Try it" as a
 *  proper labelled button. */
export function MetaActions({ anchor, presentSections }: MetaActionsProps) {
    const { endpointId } = useEndpointDocContext();
    const expandAll = useEndpointDocStore((s) => s.expandAll);
    const collapseAll = useEndpointDocStore((s) => s.collapseAll);
    const openSections = useEndpointDocStore((s) => s.openSections);

    const [linkCopied, setLinkCopied] = useState(false);
    const flashLink = useCallback(() => {
        setLinkCopied(true);
        setTimeout(() => setLinkCopied(false), 1200);
    }, []);

    const mostlyOpen = useMemo(() => {
        if (presentSections.length === 0) return false;
        let openCount = 0;
        for (const sid of presentSections) {
            if (openSections[sectionKey(endpointId, sid)]) openCount += 1;
        }
        return openCount > presentSections.length / 2;
    }, [openSections, presentSections, endpointId]);

    const copyLink = useCallback(() => {
        if (typeof window === 'undefined') return;
        const url = `${window.location.origin}${window.location.pathname}#${anchor}`;
        void navigator.clipboard?.writeText(url).then(flashLink);
    }, [anchor, flashLink]);

    const toggleAll = useCallback(() => {
        if (mostlyOpen) collapseAll(endpointId, presentSections);
        else expandAll(endpointId, presentSections);
    }, [mostlyOpen, collapseAll, expandAll, endpointId, presentSections]);

    const linkLabel = linkCopied ? 'Copied!' : 'Copy link to endpoint';
    const linkIcon = linkCopied ? (
        <Check className="h-3.5 w-3.5" />
    ) : (
        <Link2 className="h-3.5 w-3.5" />
    );
    const showToggleAll = presentSections.length >= 2;
    const toggleAllLabel = mostlyOpen ? 'Collapse all sections' : 'Expand all sections';
    const toggleAllIcon = mostlyOpen ? (
        <ChevronsDownUp className="h-3.5 w-3.5" />
    ) : (
        <ChevronsUpDown className="h-3.5 w-3.5" />
    );
    const toggleAllNode = showToggleAll ? (
        <IconButton label={toggleAllLabel} onClick={toggleAll}>
            {toggleAllIcon}
        </IconButton>
    ) : null;

    return (
        <div className="flex items-center gap-0.5">
            <IconButton label={linkLabel} onClick={copyLink} active={linkCopied}>
                {linkIcon}
            </IconButton>
            {toggleAllNode}
        </div>
    );
}

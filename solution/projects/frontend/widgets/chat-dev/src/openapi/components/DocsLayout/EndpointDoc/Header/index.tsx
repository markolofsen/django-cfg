'use client';

import { Check, Play, Sparkles } from 'lucide-react';
import React, { useCallback, useMemo, useState } from 'react';

import { Button } from '@djangocfg/ui-core/components';

import { MarkdownMessage } from '@djangocfg/widget-code/markdown-message';
import type { ApiEndpoint } from '../../../../types';
import { endpointToMarkdown } from '../../../../utils/schemaExport';
import type { SectionId } from '../types';
import { MetaActions } from './MetaActions';
import { MethodBadge } from './MethodBadge';
import { PathDisplay } from './PathDisplay';

interface EndpointHeaderProps {
    endpoint: ApiEndpoint;
    anchor: string;
    isLoadedInPlayground: boolean;
    onTryIt: () => void;
    /** Sections actually rendered on this endpoint — drives the
     *  expand/collapse-all icon in the meta row. */
    presentSections: readonly SectionId[];
}

/** Card header, three stacked rows:
 *   1. Meta — small utility strip: method badge · inline actions · Try-it.
 *   2. Path — large monospace, the visual focus of the card.
 *   3. Description — prose, aligned to the left edge under path.
 *
 *  Splitting metadata from the path lets the path itself become the
 *  focal point — readers scan paths when scrolling, not badges. The
 *  meta row stays compact so it reads as "info about this endpoint"
 *  rather than "toolbar that competes for attention". */
export function EndpointHeader({
    endpoint,
    anchor,
    isLoadedInPlayground,
    onTryIt,
    presentSections,
}: EndpointHeaderProps) {
    // Memoise the markdown dump — only recomputes when the endpoint
    // reference changes, not on unrelated re-renders of the subtree.
    const endpointMd = useMemo(() => endpointToMarkdown(endpoint), [endpoint]);

    const [aiCopied, setAiCopied] = useState(false);
    const onAiCopy = useCallback(() => {
        if (typeof window === 'undefined') return;
        void navigator.clipboard?.writeText(endpointMd).then(() => {
            setAiCopied(true);
            setTimeout(() => setAiCopied(false), 1200);
        });
    }, [endpointMd]);

    const tryItLabel = isLoadedInPlayground ? 'Loaded' : 'Try it';
    const aiCopyIcon = aiCopied ? (
        <Check className="h-3 w-3" />
    ) : (
        <Sparkles className="h-3 w-3" />
    );
    const aiCopyLabel = aiCopied ? 'Copied' : 'AI Copy';
    const descriptionNode = endpoint.description ? (
        <div className="text-muted-foreground text-sm">
            <MarkdownMessage content={endpoint.description} />
        </div>
    ) : null;

    return (
        <header className="space-y-3">
            {/* Row 1 — meta strip. Badge + inline icon actions on the
                left, primary CTAs on the right. Kept tight (24px tall)
                so it doesn't visually compete with the path row below. */}
            <div className="flex items-center gap-3 flex-wrap">
                <div className="flex items-center gap-2 min-w-0">
                    <MethodBadge method={endpoint.method} />
                    <MetaActions anchor={anchor} presentSections={presentSections} />
                </div>
                <div className="ml-auto flex items-center gap-2">
                    <Button
                        size="sm"
                        variant="secondary"
                        onClick={onAiCopy}
                        title="Copy endpoint as Markdown for AI"
                        aria-label="Copy endpoint as Markdown for AI"
                        className="h-7 text-xs gap-1.5 px-2.5"
                    >
                        {aiCopyIcon}
                        {aiCopyLabel}
                    </Button>
                    <Button
                        size="sm"
                        variant={isLoadedInPlayground ? 'secondary' : 'default'}
                        onClick={onTryIt}
                        className="h-7 text-xs gap-1.5 px-2.5"
                    >
                        <Play className="h-3 w-3" />
                        {tryItLabel}
                    </Button>
                </div>
            </div>

            {/* Row 2 — path as the visual focal point. Larger and more
                prominent than it was when competing with the badge
                and action icons inline. */}
            <div className="min-w-0">
                <PathDisplay path={endpoint.path} />
            </div>

            {/* Row 3 — description, aligned to the left edge under the
                path. Text-sm so it reads as subtitle, not body copy. */}
            {descriptionNode}
        </header>
    );
}

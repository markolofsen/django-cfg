'use client';

import { Check, ChevronDown, Sparkles } from 'lucide-react';
import React, { useCallback, useMemo, useState } from 'react';

import {
    Button,
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@djangocfg/ui-core/components';
import { toast } from '@djangocfg/ui-core/hooks';

import type { ApiEndpoint, OpenApiSchema } from '../../types';
import {
    formatBytes,
    toCompactJson,
    toMarkdown,
    toRawJson,
} from '../../utils/schemaExport';

type Flavour = 'markdown' | 'compact' | 'raw';

const FLAVOUR_LABELS: Record<Flavour, { title: string; hint: string }> = {
    markdown: {
        title: 'Markdown for LLM',
        hint: 'Endpoints + params as prose. Smallest.',
    },
    compact: {
        title: 'Compact JSON',
        hint: 'Dereferenced, no examples, minified.',
    },
    raw: {
        title: 'Raw JSON',
        hint: 'Full OpenAPI document with $refs.',
    },
};

interface SchemaCopyMenuProps {
    schema: OpenApiSchema | null;
    endpoints: ApiEndpoint[];
    /** Resolved base URL that gets embedded into the copy so the AI
     *  receives working URLs, not the ones originally in ``schema.servers``. */
    baseUrl?: string;
    /** Trigger appearance.
     *  - ``button`` (default) — labelled pill with icon + chevron.
     *  - ``icon`` — square ghost button, used in tight spots like the
     *    sidebar header where there is no room for "Copy for AI".
     *  - ``footer`` — full-width secondary CTA, designed to sit at the
     *    bottom of the sidebar. Menu opens upward so it stays inside
     *    the panel. */
    variant?: 'button' | 'icon' | 'footer';
    /** Where the dropdown content opens. Defaults to ``right`` for the
     *  inline triggers; ``footer`` overrides to ``top``. */
    side?: 'right' | 'top' | 'bottom' | 'left';
}

/**
 * Per-schema copy dropdown. Shows three flavours tuned for different LLM
 * use-cases. We compute each flavour lazily (only on click) because
 * dereferencing + stringifying a large schema can be non-trivial — sizes
 * are displayed after the first successful copy, via a tiny cache.
 */
export function SchemaCopyMenu({ schema, endpoints, baseUrl, variant = 'button', side }: SchemaCopyMenuProps) {
    const [sizeCache, setSizeCache] = useState<Partial<Record<Flavour, string>>>({});
    const [justCopied, setJustCopied] = useState<Flavour | null>(null);
    const [open, setOpen] = useState(false);

    const isReady = schema !== null && endpoints.length > 0;

    const build = useCallback(
        (flavour: Flavour): string => {
            if (!schema) return '';
            if (flavour === 'markdown') return toMarkdown(schema, endpoints, baseUrl);
            if (flavour === 'compact') return toCompactJson(schema, baseUrl);
            return toRawJson(schema, baseUrl);
        },
        [schema, endpoints, baseUrl],
    );

    const handleCopy = useCallback(
        async (flavour: Flavour) => {
            if (!isReady) return;
            const text = build(flavour);
            const label = FLAVOUR_LABELS[flavour].title;
            try {
                await navigator.clipboard.writeText(text);
                const size = formatBytes(text);
                setSizeCache((prev) => ({ ...prev, [flavour]: size }));
                setJustCopied(flavour);
                setTimeout(() => setJustCopied(null), 1500);
                setOpen(false);
                toast.success(`Copied ${label}`, { description: size });
            } catch (err) {
                const message = err instanceof Error ? err.message : 'Clipboard permission denied';
                toast.error('Copy failed', { description: message });
            }
        },
        [build, isReady],
    );

    const flavours = useMemo<Flavour[]>(() => ['markdown', 'compact', 'raw'], []);

    const resolvedSide = side ?? (variant === 'footer' ? 'top' : 'right');
    const resolvedAlign = variant === 'footer' ? 'center' : 'start';

    return (
        <DropdownMenu open={open} onOpenChange={setOpen}>
            <DropdownMenuTrigger asChild>
                {variant === 'icon' ? (
                    <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7 shrink-0"
                        disabled={!isReady}
                        title="Copy schema for AI"
                        aria-label="Copy schema for AI"
                    >
                        <Sparkles className="h-3.5 w-3.5" />
                    </Button>
                ) : variant === 'footer' ? (
                    <Button
                        variant="secondary"
                        size="sm"
                        className="w-full justify-center gap-1.5 text-xs"
                        disabled={!isReady}
                    >
                        <Sparkles className="h-3 w-3" />
                        Copy schema for AI
                        <ChevronDown className="h-3 w-3 opacity-60" />
                    </Button>
                ) : (
                    <Button variant="outline" size="sm" className="gap-1.5 text-xs" disabled={!isReady}>
                        <Sparkles className="h-3 w-3" />
                        Copy for AI
                        <ChevronDown className="h-3 w-3 opacity-60" />
                    </Button>
                )}
            </DropdownMenuTrigger>
            <DropdownMenuContent
                side={resolvedSide}
                align={resolvedAlign}
                sideOffset={6}
                collisionPadding={8}
                className="w-60 max-w-[calc(100vw-16px)]"
            >
                <DropdownMenuLabel className="text-[10px] uppercase tracking-wider text-muted-foreground/70">
                    Copy schema
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                {flavours.map((f) => {
                    const label = FLAVOUR_LABELS[f];
                    const size = sizeCache[f];
                    const isDone = justCopied === f;
                    return (
                        <DropdownMenuItem
                            key={f}
                            onClick={(e) => {
                                e.preventDefault();
                                void handleCopy(f);
                            }}
                            className="flex flex-col items-start gap-0.5 py-2 cursor-pointer"
                        >
                            <div className="flex w-full items-center gap-2">
                                <span className="text-xs font-medium flex-1">{label.title}</span>
                                {isDone ? (
                                    <span className="inline-flex items-center gap-1 text-[10px] text-success">
                                        <Check className="h-3 w-3" /> Copied
                                    </span>
                                ) : size ? (
                                    <span className="text-[10px] font-mono text-muted-foreground/70 tabular-nums">
                                        {size}
                                    </span>
                                ) : null}
                            </div>
                            <span className="text-[10px] text-muted-foreground/70 leading-snug line-clamp-1">
                                {label.hint}
                            </span>
                        </DropdownMenuItem>
                    );
                })}
            </DropdownMenuContent>
        </DropdownMenu>
    );
}

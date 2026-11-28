'use client';

import { ChevronRight } from 'lucide-react';
import React, { useState } from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import type { FieldNode } from './types';

interface FieldRowProps {
    field: FieldNode;
    /** 0-based nesting level. Used to compute left padding so the tree
     *  visually expresses hierarchy without relying on a separate tree
     *  component (no deps, one file). */
    depth: number;
    /** Parent container nodes render with an extra vertical tick so the
     *  tree reads as a rooted graph instead of flat indented rows. */
    showTreeLine?: boolean;
}

/** Recursive tree row. Object/array nodes are collapsible and default
 *  to expanded at shallow depths — readers almost always want to see
 *  the first level of nesting, and explicitly collapsing uninteresting
 *  subtrees is cheaper than expanding every interesting one. */
export function FieldRow({ field, depth, showTreeLine = true }: FieldRowProps) {
    const isExpandable = (field.kind === 'object' || field.kind === 'array') &&
        Array.isArray(field.children) && field.children.length > 0;

    // Expand levels 0-1 by default; beyond that the tree can explode
    // visually for deeply-nested objects (think Pet.category.tag.…).
    const [open, setOpen] = useState(depth < 2);

    // Inline padding via style so arbitrary depths render without a
    // pile of Tailwind classes. 14px per level matches the chevron gap
    // at smaller text sizes.
    const padLeft = showTreeLine ? depth * 14 : 0;

    const toggle = () => isExpandable && setOpen((v) => !v);

    return (
        <div className="bg-background">
            <div
                className={cn(
                    'grid grid-cols-[16px_minmax(0,1fr)] items-baseline gap-2 px-3 py-2',
                    isExpandable && 'cursor-pointer hover:bg-muted/30',
                )}
                style={{ paddingLeft: 12 + padLeft }}
                onClick={toggle}
                onKeyDown={(e) => {
                    if (!isExpandable) return;
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        toggle();
                    }
                }}
                role={isExpandable ? 'button' : undefined}
                tabIndex={isExpandable ? 0 : undefined}
                aria-expanded={isExpandable ? open : undefined}
            >
                <ChevronRight
                    className={cn(
                        'h-3.5 w-3.5 text-muted-foreground/50 shrink-0 transition-transform',
                        !isExpandable && 'opacity-0',
                        open && 'rotate-90',
                    )}
                />
                <div className="min-w-0 space-y-1">
                    <div className="flex items-baseline gap-2 flex-wrap">
                        <code className="font-mono text-xs font-medium text-foreground">
                            {field.name}
                        </code>
                        {field.required && (
                            <span
                                title="Required"
                                className="text-[9px] text-destructive font-bold leading-none"
                            >
                                *
                            </span>
                        )}
                        <code className="font-mono text-[11px] text-muted-foreground/70">
                            {field.type}
                        </code>
                    </div>
                    {field.description && (
                        <p className="text-xs text-muted-foreground leading-relaxed break-words">
                            {field.description}
                        </p>
                    )}
                    {field.enumValues && field.enumValues.length > 0 && (
                        <div className="flex flex-wrap gap-1 pt-0.5">
                            {field.enumValues.map((v) => (
                                <code
                                    key={v}
                                    className="inline-flex items-center rounded border border-border/60 bg-muted/40 px-1.5 py-px font-mono text-[10px] text-muted-foreground"
                                >
                                    {v}
                                </code>
                            ))}
                        </div>
                    )}
                </div>
            </div>
            {isExpandable && open && (
                <div>
                    {field.children!.map((child, i) => (
                        <FieldRow
                            key={`${child.name}-${i}`}
                            field={child}
                            depth={depth + 1}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}

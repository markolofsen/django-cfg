'use client';

/**
 * Shared primitive UI components used by the playground panels
 * (Request, Response) in both the slide-in and mobile-sheet surfaces.
 * Keep this file free of any business logic or context reads.
 */

import { ChevronRight } from 'lucide-react';
import React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

// ─── Style helpers ────────────────────────────────────────────────────────────
// Method/status → semantic status-token mappings live in ./http-colors and are
// re-exported here so existing imports of `./ui` keep working.
export { getMethodStyle, getStatusStyle } from './http-colors';
import { getMethodStyle, getStatusStyle } from './http-colors';

// ``relativePath`` lives in utils/url.ts now — re-exported here so every
// component that used to import it from ``./ui`` keeps working.
export { relativePath } from '../../utils/url';

// ─── Atoms ────────────────────────────────────────────────────────────────────

export function MethodBadge({ method }: { method: string }) {
    return (
        <span className={cn(
            'inline-flex shrink-0 items-center rounded border px-1.5 py-px',
            'font-mono text-[10px] font-bold uppercase tracking-wider leading-none',
            getMethodStyle(method),
        )}>
            {method}
        </span>
    );
}

export function StatusBadge({ status }: { status: number }) {
    return (
        <span className={cn(
            'inline-flex items-center rounded border px-1.5 py-px',
            'font-mono text-[11px] font-bold leading-none',
            getStatusStyle(status),
        )}>
            {status}
        </span>
    );
}

export function SectionLabel({ children }: { children: React.ReactNode }) {
    return (
        <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/60 select-none">
            {children}
        </p>
    );
}

export function Panel({ children, className }: { children: React.ReactNode; className?: string }) {
    return (
        <div className={cn('flex flex-col min-h-0 overflow-hidden', className)}>
            {children}
        </div>
    );
}

export function ScrollArea({ children, className }: { children: React.ReactNode; className?: string }) {
    return (
        <div className={cn('flex-1 overflow-y-auto min-h-0', className)}>
            {children}
        </div>
    );
}

export function PanelHeader({ title }: { title: string }) {
    return (
        <div className="shrink-0 border-b px-4 h-10 flex items-center">
            <span className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground/50">
                {title}
            </span>
        </div>
    );
}

export function EmptyState({
    icon: Icon,
    text,
    className,
}: {
    icon: React.ElementType;
    text: string;
    className?: string;
}) {
    return (
        <div
            className={cn(
                'flex flex-col items-center justify-center h-full gap-3 px-6 text-center',
                className,
            )}
        >
            <Icon className="h-7 w-7 text-muted-foreground/25" />
            <p className="text-xs text-muted-foreground">{text}</p>
        </div>
    );
}

export function CollapsibleSection({
    label,
    action,
    children,
    defaultOpen = false,
}: {
    label: React.ReactNode;
    action?: React.ReactNode;
    children: React.ReactNode;
    defaultOpen?: boolean;
}) {
    const [open, setOpen] = React.useState(defaultOpen);
    return (
        <div className="space-y-0">
            <div className="flex items-center justify-between">
                <button
                    type="button"
                    onClick={() => setOpen((v) => !v)}
                    className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/60 hover:text-muted-foreground transition-colors py-1"
                >
                    <ChevronRight className={cn('h-3 w-3 transition-transform', open && 'rotate-90')} />
                    {label}
                </button>
                {action && <div className="shrink-0">{action}</div>}
            </div>
            {open && <div>{children}</div>}
        </div>
    );
}

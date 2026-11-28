'use client';

import type { OpenApiInfo } from '../../../types';

interface BrandHeaderProps {
    info: OpenApiInfo | null;
}

/** Topmost row of the sidebar: API title on the left, tiny version
 *  tag below it. The Copy-for-AI menu used to live here as a cramped
 *  icon button; it now sits as a full-width secondary CTA in the
 *  sidebar footer where it's actually visible. */
export function BrandHeader({ info }: BrandHeaderProps) {
    const apiTitle = info?.title ?? 'API Reference';
    const versionLabel = info?.version ? `v${info.version}` : null;
    const versionNode = versionLabel ? (
        <div className="font-mono text-[10px] text-muted-foreground/60 leading-tight mt-0.5">
            {versionLabel}
        </div>
    ) : null;

    return (
        <div className="shrink-0 border-b px-3 py-2.5">
            <div
                className="text-[13px] font-semibold text-foreground leading-tight truncate"
                title={apiTitle}
            >
                {apiTitle}
            </div>
            {versionNode}
        </div>
    );
}

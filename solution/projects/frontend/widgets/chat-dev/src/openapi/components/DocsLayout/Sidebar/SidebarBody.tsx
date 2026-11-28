'use client';

import { CategoryBlock } from './CategoryBlock';
import { SchemaSection } from './SchemaSection';
import type { NavigateFn, SidebarBodyVM } from './types';

interface SidebarBodyProps {
    body: SidebarBodyVM;
    onNavigate: NavigateFn;
}

/** Scrollable body of the sidebar. Picks the rendering strategy based
 *  on ``body.kind`` — flat category list for single-schema mode,
 *  nested schema sections for multi-schema mode — and falls back to
 *  a centred empty-state message when the filter pipeline yields no
 *  rows. */
export function SidebarBody({ body, onNavigate }: SidebarBodyProps) {
    if (body.kind === 'flat') {
        if (body.categories.length === 0) {
            return (
                <div className="py-10 px-4 text-center text-xs text-muted-foreground">
                    {body.emptyText}
                </div>
            );
        }
        return (
            <nav className="pt-1.5 pb-[10vh]">
                {body.categories.map((cat) => (
                    <CategoryBlock key={cat.key} category={cat} onNavigate={onNavigate} />
                ))}
            </nav>
        );
    }

    if (body.sections.length === 0) {
        return (
            <div className="py-10 px-4 text-center text-xs text-muted-foreground">
                {body.emptyText}
            </div>
        );
    }

    return (
        <nav className="py-1.5">
            {body.sections.map((section) => (
                <SchemaSection key={section.sourceId} section={section} onNavigate={onNavigate} />
            ))}
        </nav>
    );
}

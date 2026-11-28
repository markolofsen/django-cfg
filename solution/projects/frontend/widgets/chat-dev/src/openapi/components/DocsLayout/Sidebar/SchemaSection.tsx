'use client';

import { CategoryBlock } from './CategoryBlock';
import type { NavigateFn, SchemaSectionVM } from './types';

interface SchemaSectionProps {
    section: SchemaSectionVM;
    onNavigate: NavigateFn;
}

/** One schema block inside ``sections`` grouping mode. Renders a
 *  sticky header with the schema name so users can tell which API
 *  they're looking at while scrolling, then the categories below. */
export function SchemaSection({ section, onNavigate }: SchemaSectionProps) {
    return (
        <div className="mb-4 last:mb-2">
            <div className="px-3 py-1.5 sticky top-0 z-[1] bg-background/95 backdrop-blur-[2px] border-b border-border/40">
                <span className="text-[11px] font-bold uppercase tracking-[0.12em] text-foreground/80">
                    {section.sourceName}
                </span>
            </div>
            {section.categories.map((cat) => (
                <CategoryBlock key={cat.key} category={cat} onNavigate={onNavigate} />
            ))}
        </div>
    );
}

'use client';

import React from 'react';

import { EndpointRow } from './EndpointRow';
import type { CategoryVM, NavigateFn } from './types';

interface CategoryBlockProps {
    category: CategoryVM;
    onNavigate: NavigateFn;
}

/** A labelled group of endpoint rows. The category header is
 *  deliberately tiny (text-[10px] tracking-wider) — it's a divider, not
 *  a call to attention. Users who are reading the list want to see the
 *  endpoint names, not the category prose. */
export const CategoryBlock = React.memo(function CategoryBlock({
    category,
    onNavigate,
}: CategoryBlockProps) {
    return (
        <div className="mb-2.5 last:mb-1">
            <div className="px-3 pt-3 pb-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-muted-foreground/50 select-none">
                {category.category}
            </div>
            <div>
                {category.rows.map((row) => (
                    <EndpointRow key={row.key} row={row} onNavigate={onNavigate} />
                ))}
            </div>
        </div>
    );
});

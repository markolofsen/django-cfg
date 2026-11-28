'use client';

import React, { useEffect, useRef } from 'react';

import { TooltipHint } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { MethodBadge } from '../../shared/ui';
import type { EndpointRowVM, NavigateFn } from './types';

interface EndpointRowProps {
    row: EndpointRowVM;
    onNavigate: NavigateFn;
}

/** One endpoint in the sidebar list. Layout decisions worth calling out:
 *   - Fixed 52px badge column via CSS grid so ``GET`` / ``POST`` /
 *     ``PATCH`` all take the same horizontal slot and labels align
 *     vertically on the left edge. Without this the list looks ragged
 *     because ``POST`` is wider than ``GET`` and each label starts at
 *     a different x offset.
 *   - ``items-baseline`` so the method badge sits on the same visual
 *     line as the label text, not in its vertical centre.
 *   - ``py-1`` (not the old ``py-1.5``) for higher list density.
 *   - Trailing full-stops are trimmed from the label. OpenAPI
 *     summaries often end in ``.`` which looks like noise in a list.
 *   - Active state is a single left-edge accent bar + soft tint — no
 *     big filled background so the method badge still carries the
 *     colour semantics of the row. */
export const EndpointRow = React.memo(function EndpointRow({
    row,
    onNavigate,
}: EndpointRowProps) {
    // Strip a trailing full-stop — OpenAPI ``summary`` routinely ends
    // in ``.`` which looks like punctuation noise when stacked in a list.
    const displayLabel = row.label.replace(/\.$/, '');

    // Keep the active row visible inside the sidebar's scroll container.
    // ``block: 'nearest'`` is a no-op when the row is already in view,
    // so this only fires when the user scrolled the docs far enough to
    // push the highlighted endpoint above/below the sidebar viewport.
    const buttonRef = useRef<HTMLButtonElement | null>(null);
    useEffect(() => {
        if (!row.isActive || !buttonRef.current) return;
        buttonRef.current.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    }, [row.isActive]);

    return (
        <TooltipHint tooltip={{ content: <span className="font-mono text-[11px]">{row.tooltip}</span>, side: 'right', align: 'center', delay: 350 }}>
          <button
              ref={buttonRef}
              onClick={() => onNavigate(row.anchor, row.schemaId)}
              aria-current={row.isActive ? 'location' : undefined}
              className={cn(
                  'relative w-full text-left grid grid-cols-[52px_minmax(0,1fr)] items-baseline gap-2 pl-3 pr-3 py-1 transition-colors',
                  row.isActive
                      ? 'bg-primary/10 text-foreground'
                      : 'hover:bg-muted/40 text-foreground/75 hover:text-foreground',
              )}
          >
              {row.isActive && (
                  <span className="absolute left-0 top-1 bottom-1 w-0.5 rounded-r bg-primary" />
              )}
              <span className="justify-self-start">
                  <MethodBadge method={row.method} />
              </span>
              <span
                  className={cn(
                      'line-clamp-2 leading-snug min-w-0',
                      row.useMono ? 'font-mono text-[11px] break-all' : 'text-[12px]',
                      row.isActive && 'text-foreground font-medium',
                  )}
              >
                  {displayLabel}
              </span>
          </button>
        </TooltipHint>
    );
});

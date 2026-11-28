// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import type { ApiProp } from '../types';
import { TypeDisplay } from './TypeDisplay';

interface RowProps {
  prop: ApiProp;
  showDefault: boolean;
}

/**
 * Single parameter row. Click to expand `description` / `fullType` when
 * either is present; otherwise the button is rendered disabled so the
 * row stays keyboard-accessible but doesn't pretend to be interactive.
 */
export function Row({ prop, showDefault }: RowProps) {
  const [open, setOpen] = React.useState(false);
  const hasDetails = Boolean(prop.description || prop.fullType);

  return (
    <div className="border-b border-border/40 last:border-b-0" data-slot="api-ref-row">
      <button
        type="button"
        onClick={() => hasDetails && setOpen((v) => !v)}
        disabled={!hasDetails}
        className={cn(
          'flex w-full items-center gap-4 px-4 py-3 text-left transition-colors',
          hasDetails && 'cursor-pointer hover:bg-muted/30',
          !hasDetails && 'cursor-default',
        )}
        aria-expanded={hasDetails ? open : undefined}
      >
        <span className="min-w-[180px] shrink-0 font-mono text-sm">
          <span className="text-foreground">{prop.name}</span>
          {prop.required ? (
            <span className="ml-0.5 text-destructive" aria-label="required">
              *
            </span>
          ) : (
            <span className="text-muted-foreground" aria-hidden="true">
              ?
            </span>
          )}
        </span>
        <span className="flex-1 min-w-0">
          <TypeDisplay type={prop.type} />
        </span>
        {showDefault && (
          <code
            className={cn(
              'min-w-[100px] shrink-0 font-mono text-xs',
              prop.defaultValue ? 'text-foreground' : 'text-muted-foreground',
            )}
            data-slot="api-ref-default"
          >
            {prop.defaultValue ?? '—'}
          </code>
        )}
        {hasDetails && (
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
            className={cn(
              'size-4 shrink-0 text-muted-foreground transition-transform',
              open && 'rotate-180',
            )}
          >
            <path d="m6 9 6 6 6-6" />
          </svg>
        )}
      </button>
      {open && hasDetails && (
        <div className="space-y-2 border-t border-border/30 bg-muted/20 px-4 py-3">
          {prop.description && (
            <p className="text-sm text-muted-foreground">{prop.description}</p>
          )}
          {prop.fullType && (
            <div className="flex items-baseline gap-6">
              <span className="shrink-0 text-sm text-muted-foreground">Type</span>
              <TypeDisplay type={prop.fullType} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

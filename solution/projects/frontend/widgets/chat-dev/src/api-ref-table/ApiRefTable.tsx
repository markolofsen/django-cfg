// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// API reference / props table with per-token type colorization,
// expand-on-click description rows, and an optional `Default` column.
//
// Port notes:
//   - Type-token colors map to semantic tokens (CONTRACT §2, AUDIT §6):
//     string→success, number→warning, boolean→info, function→destructive,
//     reactnode→info, enum→categorical (chart-3 var), nullish→muted-fg,
//     primary→primary.
//   - Required marker switched from a trailing `?` (optional indicator
//     in the source) to a leading `*` in `text-destructive` for required
//     rows; optionals keep the muted `?`.
//   - Default-value chip is monospace on `bg-muted/40 border-border`.
//   - No nested providers (CONTRACT §5); no motion (CONTRACT §4).

'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import type { ApiRefTableProps } from './types';
import { Row } from './components/Row';

export function ApiRefTable({
  title,
  props: rows,
  nameLabel = 'Prop',
  showDefaults,
  emptyMessage = 'No parameters.',
  className,
  ...rest
}: ApiRefTableProps) {
  const showDefault = showDefaults ?? rows.some((r) => r.defaultValue != null);

  return (
    <div
      data-slot="api-ref-table"
      className={cn(
        'overflow-hidden rounded-xl border border-border bg-card shadow-sm',
        className,
      )}
      {...rest}
    >
      {title && (
        <div className="border-b border-border/40 px-4 py-3">
          <h3 className="text-lg font-semibold tracking-tight text-foreground">{title}</h3>
        </div>
      )}
      <div className="flex items-center gap-4 border-b border-border/40 bg-muted/40 px-4 py-2.5 text-sm font-medium text-muted-foreground">
        <span className="min-w-[180px] shrink-0">{nameLabel}</span>
        <span className="flex-1 min-w-0">Type</span>
        {showDefault && <span className="min-w-[100px] shrink-0">Default</span>}
        {/* spacer matching the chevron column to keep header cells aligned */}
        <span className="size-4 shrink-0" aria-hidden="true" />
      </div>
      {rows.length === 0 ? (
        <div className="px-4 py-6 text-center text-sm text-muted-foreground">
          {emptyMessage}
        </div>
      ) : (
        rows.map((prop) => <Row key={prop.name} prop={prop} showDefault={showDefault} />)
      )}
    </div>
  );
}

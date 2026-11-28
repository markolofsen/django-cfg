// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// Operational status badge with colored dot and label for dashboards,
// status pages, and header bars.
//
// Golden sample — see CONTRACT.md. Demonstrates:
//   - semantic tokens only (no raw color scales)
//   - Tailwind `animate-ping` for pulse (no framer-motion)
//   - attribution header
//   - no nested providers
//   - decomposed types in `./types`, lazy in `./lazy`

'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import {
  STATUS_CONFIG,
  TONE_CLASSES,
  statusIndicatorVariants,
  type StatusIndicatorProps,
  type StatusTone,
} from './types';

const LIVE_STATUSES = new Set<string>([
  'incident',
  'major-outage',
  'partial-outage',
  'degraded',
]);

export function StatusIndicator({
  status,
  label,
  tone: toneProp,
  pulse: pulseProp,
  size,
  className,
  ...props
}: StatusIndicatorProps) {
  const config = STATUS_CONFIG[status];
  const tone: StatusTone = toneProp ?? config.tone;
  const displayLabel = label ?? config.label;
  const pulse = pulseProp ?? LIVE_STATUSES.has(status);

  const toneClasses = TONE_CLASSES[tone];

  return (
    <span
      data-slot="status-indicator"
      data-status={status}
      data-tone={tone}
      role="status"
      aria-label={displayLabel}
      className={cn(
        statusIndicatorVariants({ size }),
        'border-border/60 shadow-xs',
        toneClasses.pill,
        className,
      )}
      {...props}
    >
      <span
        data-slot="status-dot"
        className={cn('relative shrink-0 rounded-full', toneClasses.dot)}
        aria-hidden="true"
      >
        {pulse && (
          <span
            data-slot="status-dot-pulse"
            className={cn(
              'absolute inset-0 rounded-full opacity-60 animate-ping',
              toneClasses.dot,
            )}
          />
        )}
      </span>
      <span className={cn('whitespace-nowrap', toneClasses.text)}>
        {displayLabel}
      </span>
    </span>
  );
}

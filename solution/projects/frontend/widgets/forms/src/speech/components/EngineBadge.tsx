'use client';

import type * as React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

export interface EngineBadgeProps {
  engineId: string;
  className?: string;
}

const LABELS: Record<string, string> = {
  webspeech: 'Web Speech',
  http: 'Custom HTTP',
  websocket: 'WebSocket',
};

export function EngineBadge({ engineId, className }: EngineBadgeProps): React.ReactElement {
  const label = LABELS[engineId] ?? engineId;
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border border-border bg-muted/60 px-2 py-0.5 text-[10px] uppercase tracking-wide text-muted-foreground',
        className,
      )}
    >
      {label}
    </span>
  );
}

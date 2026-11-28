'use client';

import type * as React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

export interface PushToTalkHintProps {
  /** Same chord string passed to `usePushToTalk`. */
  chord: string;
  className?: string;
}

/**
 * Renders "Hold ⌥ to talk" with the chord pretty-printed. Tiny helper
 * meant to live next to a `DictationButton`.
 */
export function PushToTalkHint({ chord, className }: PushToTalkHintProps): React.ReactElement {
  const formatted = chord
    .split('+')
    .map((p) => p.trim().toLowerCase())
    .map((p) => {
      switch (p) {
        case 'mod':
        case 'meta':
          return '⌘';
        case 'alt':
          return '⌥';
        case 'shift':
          return '⇧';
        case 'ctrl':
          return '⌃';
        default:
          return p.length === 1 ? p.toUpperCase() : p;
      }
    })
    .join('');
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 text-[11px] text-muted-foreground',
        className,
      )}
    >
      Hold
      <kbd className="rounded border border-border bg-muted px-1 py-0.5 font-mono text-[10px] text-foreground">
        {formatted}
      </kbd>
      to talk
    </span>
  );
}

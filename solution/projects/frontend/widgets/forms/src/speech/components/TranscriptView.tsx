'use client';

import type * as React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import type { Transcript } from '../types';

export interface TranscriptViewProps {
  transcript: Transcript;
  /** Render the empty state when there is nothing yet. */
  emptyState?: React.ReactNode;
  /** Tone the interim text down so users can tell it's still "wet". */
  dimInterim?: boolean;
  className?: string;
}

/**
 * Two-tone transcript: final segments in foreground, the trailing
 * interim chunk dimmed so users see the model "thinking". Pure
 * presentational — pair with `useSpeechRecognition().transcript`.
 */
export function TranscriptView({
  transcript,
  emptyState,
  dimInterim = true,
  className,
}: TranscriptViewProps): React.ReactElement {
  const { final, interim } = transcript;
  if (!final && !interim) {
    return (
      <div className={cn('text-sm text-muted-foreground', className)}>
        {emptyState ?? 'Press the mic to start dictating…'}
      </div>
    );
  }
  return (
    <div className={cn('text-sm leading-relaxed', className)}>
      <span className="text-foreground whitespace-pre-wrap">{final}</span>
      {interim && (
        <>
          {' '}
          <span
            className={cn(
              'whitespace-pre-wrap',
              dimInterim ? 'text-muted-foreground' : 'text-foreground',
            )}
          >
            {interim}
          </span>
        </>
      )}
    </div>
  );
}

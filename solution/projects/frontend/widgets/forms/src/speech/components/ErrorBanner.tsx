'use client';

import type * as React from 'react';

import { AlertTriangle } from 'lucide-react';

import { cn } from '@djangocfg/ui-core/lib';

import type { RecognitionError } from '../types';

const FRIENDLY: Record<RecognitionError['code'], string> = {
  unsupported: 'Speech recognition isn\'t available in this browser.',
  'permission-denied': 'Microphone access was denied. Allow it in your browser settings to dictate.',
  'no-microphone': 'No microphone found.',
  network: 'Network error talking to the speech service.',
  aborted: 'Recognition was interrupted.',
  'no-speech': 'No speech was detected. Try again.',
  language: 'The requested language isn\'t supported by the engine.',
  engine: 'The speech engine reported an error.',
  unknown: 'Something went wrong with the microphone.',
};

export interface ErrorBannerProps {
  error: RecognitionError | null;
  className?: string;
  onDismiss?: () => void;
}

export function ErrorBanner({ error, className, onDismiss }: ErrorBannerProps): React.ReactElement | null {
  if (!error) return null;
  return (
    <div
      role="alert"
      className={cn(
        'flex items-start gap-2 rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-xs text-destructive',
        className,
      )}
    >
      <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
      <div className="flex-1">{FRIENDLY[error.code] ?? error.message}</div>
      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          className="text-destructive hover:underline"
        >
          Dismiss
        </button>
      )}
    </div>
  );
}

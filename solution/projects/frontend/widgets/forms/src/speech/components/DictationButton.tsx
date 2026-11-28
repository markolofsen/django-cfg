'use client';

import type * as React from 'react';

import { Loader2, Mic, MicOff } from 'lucide-react';
import type { CSSProperties, ReactNode } from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import type { RecognitionStatus } from '../types';

export interface DictationButtonProps {
  status: RecognitionStatus;
  onClick: () => void;
  isSupported?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  style?: CSSProperties;
  ariaLabel?: string;
  /** Override icon for the idle state. */
  idleIcon?: ReactNode;
  /** Override icon for the listening state. */
  listeningIcon?: ReactNode;
  /** Disable without unmounting. */
  disabled?: boolean;
}

const SIZE_CLS: Record<NonNullable<DictationButtonProps['size']>, string> = {
  sm: 'h-8 w-8 [&_svg]:h-4 [&_svg]:w-4',
  md: 'h-10 w-10 [&_svg]:h-5 [&_svg]:w-5',
  lg: 'h-12 w-12 [&_svg]:h-6 [&_svg]:w-6',
};

/**
 * Round microphone button. Cycles icon by status; shows a soft pulse
 * ring when listening. ARIA-correct so screen readers announce
 * "recording" vs "start dictation".
 */
export function DictationButton({
  status,
  onClick,
  isSupported = true,
  size = 'md',
  className,
  style,
  ariaLabel,
  idleIcon,
  listeningIcon,
  disabled,
}: DictationButtonProps): React.ReactElement {
  const listening = status === 'listening' || status === 'starting';
  const stopping = status === 'stopping';
  const off = !isSupported;

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled || off}
      aria-pressed={listening}
      aria-label={
        ariaLabel ?? (listening ? 'Stop dictation' : off ? 'Dictation not supported' : 'Start dictation')
      }
      className={cn(
        'relative inline-flex items-center justify-center rounded-full transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
        'disabled:cursor-not-allowed disabled:opacity-50',
        SIZE_CLS[size],
        listening
          ? 'bg-destructive text-destructive-foreground hover:bg-destructive/90'
          : 'bg-primary text-primary-foreground hover:bg-primary/90',
        className,
      )}
      style={style}
    >
      {listening && (
        <span
          aria-hidden
          className="absolute inset-0 rounded-full bg-destructive/40 animate-ping"
        />
      )}
      {stopping ? (
        <Loader2 className="animate-spin" />
      ) : off ? (
        listeningIcon ?? <MicOff />
      ) : listening ? (
        listeningIcon ?? <Mic />
      ) : (
        idleIcon ?? <Mic />
      )}
    </button>
  );
}

'use client';

import type * as React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

export interface RecordingPulseProps {
  /** When false the overlay is fully hidden (no DOM cost, no animation). */
  active: boolean;
  /**
   * Live RMS mic level 0..1 (from `useMicLevel` / `useSpeechRecognition`).
   * Drives the pulse amplitude so the ring "breathes" with the voice.
   * Omit for a steady ambient pulse.
   */
  level?: number;
  /** Tailwind colour token for the ring. @default 'bg-destructive' */
  tone?: string;
  className?: string;
}

/**
 * Pulsing circle overlay that signals an active recording — Gemini-style
 * `circle-overlay`. Sits absolutely over a round mic button (`inset-0`),
 * so the parent must be `relative`.
 *
 * Two layers: a steady `animate-ping` halo for the "still recording"
 * baseline, plus a level-driven ring that scales with mic amplitude so
 * loud speech visibly bumps the pulse. Pointer-events are off — the
 * button underneath stays fully clickable.
 */
export function RecordingPulse({
  active,
  level = 0,
  tone = 'bg-destructive',
  className,
}: RecordingPulseProps): React.ReactElement | null {
  if (!active) return null;

  // Map RMS 0..1 → a calm 1.0–1.45 scale. Speech rarely exceeds ~0.5
  // RMS, so we amplify the low end for a lively-but-not-jittery ring.
  const amp = Math.min(1, Math.max(0, level));
  const scale = 1 + Math.min(0.45, amp * 0.9);
  const glowOpacity = 0.25 + Math.min(0.35, amp * 0.7);

  return (
    <span aria-hidden className={cn('pointer-events-none absolute inset-0', className)}>
      {/* Steady halo — guarantees visible feedback even in silence. */}
      <span className={cn('absolute inset-0 rounded-full opacity-30 animate-ping', tone)} />
      {/* Amplitude ring — scales smoothly with the live mic level. */}
      <span
        className={cn(
          'absolute inset-0 rounded-full transition-transform duration-100 ease-out',
          tone,
        )}
        style={{ transform: `scale(${scale})`, opacity: glowOpacity }}
      />
    </span>
  );
}

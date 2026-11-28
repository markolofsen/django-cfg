'use client';

import type * as React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

export interface MicMeterProps {
  /** RMS level 0..1 (use the value returned by `useMicLevel`). */
  level: number;
  /** Number of bars rendered. @default 12 */
  bars?: number;
  /** Bar gap in px. @default 2 */
  gap?: number;
  /** Bar width in px. @default 3 */
  barWidth?: number;
  /** Container height in px. @default 24 */
  height?: number;
  className?: string;
}

/**
 * Discrete-bar VU meter — small, dependency-free, no canvas. Each bar
 * lights up when the current `level` exceeds its threshold. Centre bars
 * are tallest so the meter reads like a classic mic level indicator.
 */
export function MicMeter({
  level,
  bars = 12,
  gap = 2,
  barWidth = 3,
  height = 24,
  className,
}: MicMeterProps): React.ReactElement {
  const clamped = Math.min(1, Math.max(0, level));
  return (
    <div
      role="meter"
      aria-valuemin={0}
      aria-valuemax={1}
      aria-valuenow={clamped}
      className={cn('inline-flex items-center', className)}
      style={{ gap, height }}
    >
      {Array.from({ length: bars }).map((_, i) => {
        const ratio = (i + 1) / bars;
        const active = clamped >= ratio - 0.5 / bars;
        // taller in the middle, shorter at edges
        const heightRatio = 1 - Math.abs(i - (bars - 1) / 2) / ((bars - 1) / 2 || 1);
        const barH = Math.max(2, height * (0.35 + heightRatio * 0.65));
        return (
          <span
            key={i}
            className={cn(
              'rounded-sm transition-colors',
              active ? 'bg-primary' : 'bg-border',
            )}
            style={{ width: barWidth, height: barH }}
          />
        );
      })}
    </div>
  );
}

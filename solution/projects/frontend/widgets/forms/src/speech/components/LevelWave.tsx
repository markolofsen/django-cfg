'use client';

import type * as React from 'react';
import { useEffect, useRef, useState } from 'react';

import { cn } from '@djangocfg/ui-core/lib';

export interface LevelWaveProps {
  /** Live RMS level 0..1 (`useSpeechRecognition().level`). */
  level: number;
  /** Sampling running? History freezes (and resets on restart) when false. */
  active: boolean;
  /** Number of history bars. @default 24 */
  bars?: number;
  /** Sample interval in ms. @default 120 */
  sampleMs?: number;
  /** Strip height in px. @default 16 */
  height?: number;
  className?: string;
}

/**
 * Rolling waveform strip — the claude.ai recording-bar look. Samples
 * `level` on a fixed interval into a scrolling history: newest sample
 * on the right, quiet moments render as dots, speech as tall bars.
 * Pure DOM (no canvas), sized for inline composer use.
 */
export function LevelWave({
  level,
  active,
  bars = 24,
  sampleMs = 120,
  height = 16,
  className,
}: LevelWaveProps): React.ReactElement {
  const [history, setHistory] = useState<number[]>([]);
  const levelRef = useRef(level);
  levelRef.current = level;

  useEffect(() => {
    if (!active) {
      setHistory([]);
      return undefined;
    }
    const id = window.setInterval(() => {
      setHistory((prev) => {
        const next = [...prev, levelRef.current];
        return next.length > bars ? next.slice(next.length - bars) : next;
      });
    }, sampleMs);
    return () => {
      window.clearInterval(id);
    };
  }, [active, bars, sampleMs]);

  const cells = Array.from({ length: bars }, (_, i) => {
    const idx = history.length - bars + i;
    return idx >= 0 ? (history[idx] ?? 0) : 0;
  });

  return (
    <div
      aria-hidden
      className={cn('inline-flex items-center gap-[2px]', className)}
      style={{ height }}
    >
      {cells.map((v, i) => {
        const clamped = Math.min(1, Math.max(0, v));
        // 2px floor renders silence as a dotted baseline, claude-style —
        // dimmed hard so a quiet room reads as calm, not as visual noise.
        const barH = Math.max(2, Math.round(clamped * height));
        const silent = barH <= 2;
        return (
          <span
            key={i}
            className={cn(
              'w-[2px] rounded-full bg-current',
              silent ? 'opacity-25' : 'opacity-80',
            )}
            style={{ height: barH }}
          />
        );
      })}
    </div>
  );
}

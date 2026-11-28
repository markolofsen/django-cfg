'use client';

import type * as React from 'react';
import { useEffect, useRef } from 'react';

import { cn } from '@djangocfg/ui-core/lib';

export interface VoiceBarsProps {
  /** Live RMS level 0..1 (`useSpeechRecognition().level`). */
  level: number;
  /** Number of bars. @default 4 */
  bars?: number;
  /** Max bar height in px. @default 14 */
  height?: number;
  /** Bar width in px. @default 2.5 */
  barWidth?: number;
  className?: string;
}

/** Per-bar animation speed (rad/s) — co-prime-ish so bars never sync. */
const SPEEDS = [5.3, 7.1, 6.2, 8.3, 5.9, 7.7];

/**
 * The voice-recorder-app equalizer, miniaturised to live INSIDE the
 * record button: a few vertical bars whose heights dance with the live
 * mic level. Replaces the static mic glyph while recording (owner
 * call, 2026-08-03) — the practice every dictaphone app converged on,
 * so it needs no explanation.
 *
 * Each bar mixes the low-passed level with its own sine phase, so
 * speech reads as organic dancing rather than N copies of the same
 * bar. rAF writes heights straight to the DOM — no per-frame renders.
 */
export function VoiceBars({
  level,
  bars = 4,
  height = 14,
  barWidth = 2.5,
  className,
}: VoiceBarsProps): React.ReactElement {
  const wrapRef = useRef<HTMLSpanElement>(null);
  const levelRef = useRef(level);
  levelRef.current = level;

  useEffect(() => {
    let raf = 0;
    let smooth = 0;
    let last = performance.now();
    const tick = (now: number): void => {
      const dt = Math.min(0.1, (now - last) / 1000);
      last = now;
      // Fast attack, slower release — speech pops in, decays smoothly.
      const target = levelRef.current;
      const rate = target > smooth ? 18 : 6;
      smooth += (target - smooth) * Math.min(1, dt * rate);

      const t = now / 1000;
      // Perceptual gain: normal speech RMS sits around 0.1–0.3, which a
      // linear map wastes on the bottom quarter of the bar. The square
      // root stretches quiet levels, ×2.2 lets ordinary speech reach
      // full height (owner report: bars barely reacted to amplitude).
      const drive = Math.min(1, Math.sqrt(smooth) * 2.2);
      const nodes = wrapRef.current?.children;
      if (nodes) {
        for (let i = 0; i < nodes.length; i += 1) {
          const speed = SPEEDS[i % SPEEDS.length]!;
          const phase = (i * Math.PI * 2) / nodes.length;
          const dance = 0.45 + 0.55 * Math.abs(Math.sin(t * speed + phase));
          const h = Math.max(3, Math.round(height * drive * dance));
          (nodes[i] as HTMLElement).style.height = `${Math.min(height, h)}px`;
        }
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [height]);

  return (
    <span
      ref={wrapRef}
      aria-hidden
      className={cn('inline-flex items-center justify-center gap-[2.5px]', className)}
      style={{ height }}
    >
      {Array.from({ length: bars }).map((_, i) => (
        <span
          key={i}
          className="rounded-full bg-current"
          style={{ width: barWidth, height: 3 }}
        />
      ))}
    </span>
  );
}

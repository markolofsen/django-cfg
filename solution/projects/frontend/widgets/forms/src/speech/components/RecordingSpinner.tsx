'use client';

import type * as React from 'react';
import { useEffect, useRef } from 'react';
import { Loader2 } from 'lucide-react';

import { cn } from '@djangocfg/ui-core/lib';

export interface RecordingSpinnerProps {
  /** Live RMS level 0..1 (`useSpeechRecognition().level`). */
  level: number;
  /** Icon size in px. @default 16 */
  size?: number;
  className?: string;
}

/** Idle rotation, degrees per second — visibly alive but calm. */
const BASE_SPEED = 40;
/** Extra speed at full level — speech makes it visibly spin up. */
const LEVEL_SPEED = 900;

/**
 * Voice-activity spinner — the recording indicator that replaced the
 * bar equalizer (owner call, 2026-08-03): one arc that spins SLOWLY in
 * silence and visibly spins up while the user speaks. One element, no
 * layout width, reads instantly.
 *
 * Driven by rAF writing `transform` directly to the DOM: CSS
 * `animation-duration` restarts the animation on every change and
 * per-frame `setState` would re-render the whole slot. The incoming
 * level is low-pass smoothed so the speed feels organic, not jittery.
 */
export function RecordingSpinner({
  level,
  size = 16,
  className,
}: RecordingSpinnerProps): React.ReactElement {
  const ref = useRef<HTMLSpanElement>(null);
  const levelRef = useRef(level);
  levelRef.current = level;

  useEffect(() => {
    let raf = 0;
    let angle = 0;
    let smooth = 0;
    let last = performance.now();
    const tick = (now: number): void => {
      const dt = Math.min(0.1, (now - last) / 1000);
      last = now;
      // Low-pass toward the live level (~8Hz response).
      smooth += (levelRef.current - smooth) * Math.min(1, dt * 8);
      angle = (angle + (BASE_SPEED + smooth * LEVEL_SPEED) * dt) % 360;
      const el = ref.current;
      if (el) {
        el.style.transform = `rotate(${angle}deg)`;
        // Louder = brighter, so the spinner signals activity even at a
        // glance where rotation speed is hard to judge.
        el.style.opacity = String(0.45 + Math.min(0.55, smooth * 1.6));
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);

  return (
    <span
      ref={ref}
      aria-hidden
      className={cn('inline-flex items-center justify-center', className)}
      style={{ width: size, height: size }}
    >
      <Loader2 style={{ width: size, height: size }} />
    </span>
  );
}

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

export interface CountdownState {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  isExpired: boolean;
  totalSeconds: number;
  /**
   * Human-readable label that adapts to scale:
   * - < 1 min  → "42s"
   * - < 1 hour → "MM:SS"  e.g. "19:05"
   * - ≥ 1 hour → "Hh Mm"  e.g. "11h 52m"
   */
  label: string;
}

const ZERO_STATE: CountdownState = {
  days: 0,
  hours: 0,
  minutes: 0,
  seconds: 0,
  isExpired: true,
  totalSeconds: 0,
  label: '',
};

function formatLabel(diff: number): string {
  if (diff < 60) return `${diff}s`;
  if (diff < 3600) {
    const m = Math.floor(diff / 60);
    const s = diff % 60;
    return `${m}:${String(s).padStart(2, '0')}`;
  }
  const h = Math.floor(diff / 3600);
  const m = Math.floor((diff % 3600) / 60);
  return m > 0 ? `${h}h ${m}m` : `${h}h`;
}

function secondsToState(diff: number): CountdownState {
  if (diff <= 0) return ZERO_STATE;
  return {
    days: Math.floor(diff / (24 * 60 * 60)),
    hours: Math.floor((diff % (24 * 60 * 60)) / (60 * 60)),
    minutes: Math.floor((diff % (60 * 60)) / 60),
    seconds: diff % 60,
    isExpired: false,
    totalSeconds: diff,
    label: formatLabel(diff),
  };
}

/**
 * Date-based countdown (existing API).
 * Re-calculates every second against a UTC date string, converted to local time.
 */
export const useCountdown = (targetDate: string | null): CountdownState => {
  const [countdown, setCountdown] = useState<CountdownState>(ZERO_STATE);

  useEffect(() => {
    if (!targetDate) return;

    // Plain `Date` arithmetic, not moment: the hook only ever needed the gap in
    // seconds, and the conversion moment did (`.utc().local()`) is what a Date
    // already is internally — an absolute instant, rendered in local time only
    // when formatted. Importing moment for this shipped its 137 locale files to
    // every consumer of this package's barrel export.
    //
    // A timestamp with no zone designator means UTC here, so append the `Z`
    // that `Date` would otherwise read as local time.
    const iso = /(?:Z|[+-]\d{2}:?\d{2})$/.test(targetDate)
      ? targetDate
      : `${targetDate}Z`;
    const targetMs = new Date(iso).getTime();
    if (Number.isNaN(targetMs)) return;

    const tick = () => {
      const diff = Math.round((targetMs - Date.now()) / 1000);
      setCountdown(secondsToState(diff));
    };

    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [targetDate]);

  return countdown;
};

/**
 * Imperative seconds-based countdown with full state breakdown.
 *
 * @returns `[state, start]`
 *   - `state` — current countdown state (days/hours/minutes/seconds/isExpired/totalSeconds/label)
 *   - `start(n)` — begin/restart countdown from n seconds
 *
 * Alias: `useSecondsCountdown` (simple `[seconds, start]`)
 */
export const useCountdownFromSeconds = (): [CountdownState, (seconds: number) => void] => {
  const [state, setState] = useState<CountdownState>(ZERO_STATE);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const clear = useCallback(() => {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const start = useCallback(
    (initial: number) => {
      clear();
      setState(secondsToState(initial));
      intervalRef.current = setInterval(() => {
        setState((prev) => {
          if (prev.totalSeconds <= 1) {
            clear();
            return ZERO_STATE;
          }
          return secondsToState(prev.totalSeconds - 1);
        });
      }, 1000);
    },
    [clear],
  );

  useEffect(() => clear, [clear]);

  return [state, start];
};

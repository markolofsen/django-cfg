'use client';

/**
 * useIdleChrome - Auto-hides floating lightbox chrome when the pointer rests.
 *
 * macOS Quick Look / Preview hide their controls after a short idle period and
 * bring them back on the slightest pointer movement. This hook tracks that
 * "active" flag and gives back the pointer handlers to wire onto the canvas.
 */

import { useCallback, useEffect, useRef, useState } from 'react';

import { CHROME_IDLE_MS } from '../utils';

export interface UseIdleChromeReturn {
  /** True while the chrome should be visible (recent pointer activity). */
  active: boolean;
  /** Pointer-move handler — call to mark activity (resets the idle timer). */
  onActivity: () => void;
  /** Pin the chrome open (e.g. while hovering a control) regardless of idle. */
  setPinned: (pinned: boolean) => void;
}

export function useIdleChrome(enabled: boolean): UseIdleChromeReturn {
  const [active, setActive] = useState(true);
  const pinnedRef = useRef(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clear = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const schedule = useCallback(() => {
    clear();
    if (!enabled) return;
    timerRef.current = setTimeout(() => {
      if (!pinnedRef.current) setActive(false);
    }, CHROME_IDLE_MS);
  }, [clear, enabled]);

  const onActivity = useCallback(() => {
    setActive(true);
    schedule();
  }, [schedule]);

  const setPinned = useCallback(
    (pinned: boolean) => {
      pinnedRef.current = pinned;
      if (pinned) {
        clear();
        setActive(true);
      } else {
        schedule();
      }
    },
    [clear, schedule],
  );

  // Start the idle countdown on mount; chrome shows briefly then fades.
  useEffect(() => {
    if (!enabled) {
      setActive(true);
      return;
    }
    schedule();
    return clear;
  }, [enabled, schedule, clear]);

  return { active, onActivity, setPinned };
}

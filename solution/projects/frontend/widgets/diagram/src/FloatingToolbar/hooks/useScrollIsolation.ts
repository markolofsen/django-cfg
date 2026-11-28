'use client';

import { useCallback, useEffect, useState } from 'react';

const UNLOCKED_CLASS = 'scroll-unlocked';

/**
 * Scroll isolation — prevents the container from capturing wheel scroll
 * until the user explicitly clicks inside it (like Google Maps).
 *
 * Locked (overlay visible): wheel events on container scroll the PAGE.
 * Unlocked: normal scroll inside the container.
 *
 * Unlock: click anywhere inside the container.
 * Re-lock: click outside the container.
 *
 * When unlocked, adds `scroll-unlocked` class to the container element
 * so it can be styled (e.g. focus ring) via CSS.
 */
export function useScrollIsolation(
  ref: React.RefObject<HTMLElement | null>,
  enabled: boolean,
) {
  const [locked, setLocked] = useState(true);

  const unlock = useCallback(() => setLocked(false), []);

  // Re-lock when clicking outside the container
  useEffect(() => {
    if (!enabled) return;

    const handleDocClick = (e: MouseEvent) => {
      const el = ref.current;
      if (!el) return;
      if (!el.contains(e.target as Node)) {
        setLocked(true);
      }
    };

    document.addEventListener('click', handleDocClick, true);
    return () => document.removeEventListener('click', handleDocClick, true);
  }, [enabled, ref]);

  // Toggle class on container to allow CSS-driven focus ring
  useEffect(() => {
    const el = ref.current;
    if (!el || !enabled) return;
    if (locked) {
      el.classList.remove(UNLOCKED_CLASS);
    } else {
      el.classList.add(UNLOCKED_CLASS);
    }
    return () => el.classList.remove(UNLOCKED_CLASS);
  }, [locked, enabled, ref]);

  // Reset to locked when feature toggled on
  useEffect(() => {
    if (enabled) setLocked(true);
  }, [enabled]);

  return { locked, unlock };
}

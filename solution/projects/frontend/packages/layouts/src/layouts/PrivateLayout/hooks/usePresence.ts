/**
 * Presence: keeps an element mounted for `exitMs` after `open` turns false, so its exit
 * animation can run. With `prefers-reduced-motion` the exit is skipped (unmount at once).
 */

'use client';

import { useEffect, useState } from 'react';

import { useMediaQuery } from '@djangocfg/ui-core/hooks';

import { SIDEBAR_MOTION_MS } from '../geometry';

export interface Presence {
  /** Render the element. */
  mounted: boolean;
  /** Drives `data-state`: `open` while entering/shown, `closed` while exiting. */
  state: 'open' | 'closed';
}

export function usePresence(open: boolean, exitMs: number = SIDEBAR_MOTION_MS): Presence {
  const reduced = useMediaQuery('(prefers-reduced-motion: reduce)');
  const [lingering, setLingering] = useState(false);

  useEffect(() => {
    if (open) {
      setLingering(true);
      return;
    }
    if (reduced || exitMs <= 0) {
      setLingering(false);
      return;
    }
    const t = setTimeout(() => setLingering(false), exitMs);
    return () => clearTimeout(t);
  }, [open, reduced, exitMs]);

  return { mounted: open || lingering, state: open ? 'open' : 'closed' };
}

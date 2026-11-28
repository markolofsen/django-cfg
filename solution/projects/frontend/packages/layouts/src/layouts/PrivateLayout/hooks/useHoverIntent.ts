/**
 * Hover intent: open only after the pointer has rested for `openDelay`, close only after it has
 * been away for `closeDelay`. A pass-by shorter than `openDelay` never opens; a quick trip out
 * and back within `closeDelay` never closes. Touch pointers are ignored.
 */

'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import { HOVER_CLOSE_DELAY_MS, HOVER_OPEN_DELAY_MS } from '../geometry';

export interface HoverIntentOptions {
  openDelay?: number;
  closeDelay?: number;
  /** False (touch device, docked sidebar): never opens, and closes an open panel at once. */
  enabled?: boolean;
}

interface PointerHandlers {
  onPointerEnter: (e: { pointerType?: string }) => void;
  onPointerLeave: (e: { pointerType?: string }) => void;
}

export interface HoverIntent {
  open: boolean;
  /** For the hot zone: enter starts the open timer, leave schedules the close. */
  zoneProps: PointerHandlers;
  /** For the opened panel: enter opens/keeps at once, leave schedules the close. */
  panelProps: PointerHandlers;
  /** Close at once. */
  close: () => void;
  /** Hold open (a menu launched from the panel is open); releasing schedules the close. */
  pin: (pinned: boolean) => void;
}

export function useHoverIntent({
  openDelay = HOVER_OPEN_DELAY_MS,
  closeDelay = HOVER_CLOSE_DELAY_MS,
  enabled = true,
}: HoverIntentOptions = {}): HoverIntent {
  const [open, setOpen] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pinned = useRef(false);
  const openRef = useRef(false);

  const set = useCallback((value: boolean) => {
    openRef.current = value;
    setOpen(value);
  }, []);

  const cancel = useCallback(() => {
    if (timer.current) clearTimeout(timer.current);
    timer.current = null;
  }, []);

  const scheduleClose = useCallback(() => {
    cancel();
    if (!openRef.current || pinned.current) return;
    timer.current = setTimeout(() => set(false), closeDelay);
  }, [cancel, closeDelay, set]);

  const close = useCallback(() => {
    cancel();
    set(false);
  }, [cancel, set]);

  const pin = useCallback(
    (value: boolean) => {
      pinned.current = value;
      if (value) cancel();
      else scheduleClose();
    },
    [cancel, scheduleClose],
  );

  const zoneProps = useMemo<PointerHandlers>(
    () => ({
      onPointerEnter: (e) => {
        if (!enabled || e.pointerType === 'touch') return;
        cancel();
        if (openRef.current) return;
        timer.current = setTimeout(() => set(true), openDelay);
      },
      onPointerLeave: (e) => {
        if (e.pointerType === 'touch') return;
        scheduleClose();
        // Not open yet: leaving cancels the pending open (cancel ran in scheduleClose).
      },
    }),
    [enabled, cancel, scheduleClose, set, openDelay],
  );

  const panelProps = useMemo<PointerHandlers>(
    () => ({
      onPointerEnter: () => {
        cancel();
        if (enabled) set(true);
      },
      onPointerLeave: () => scheduleClose(),
    }),
    [enabled, cancel, scheduleClose, set],
  );

  useEffect(() => {
    if (!enabled) close();
  }, [enabled, close]);

  useEffect(() => cancel, [cancel]);

  return { open: enabled && open, zoneProps, panelProps, close, pin };
}

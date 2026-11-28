'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

export interface UseDropdownMenuReturn {
  openDropdownKey: string | null;
  scheduleOpen: (key: string) => void;
  scheduleClose: (key: string) => void;
  closeDropdown: () => void;
}

/** Hover-based open/close with debounce timers for desktop dropdown menus. */
export function useDropdownMenu(): UseDropdownMenuReturn {
  const [openDropdownKey, setOpenDropdownKey] = useState<string | null>(null);
  const openTimerRef = useRef<number | null>(null);
  const closeTimerRef = useRef<number | null>(null);

  const clearOpenTimer = useCallback(() => {
    if (openTimerRef.current !== null) {
      window.clearTimeout(openTimerRef.current);
      openTimerRef.current = null;
    }
  }, []);

  const clearCloseTimer = useCallback(() => {
    if (closeTimerRef.current !== null) {
      window.clearTimeout(closeTimerRef.current);
      closeTimerRef.current = null;
    }
  }, []);

  const scheduleOpen = useCallback((key: string) => {
    clearOpenTimer();
    clearCloseTimer();
    openTimerRef.current = window.setTimeout(() => {
      setOpenDropdownKey(key);
    }, 80);
  }, [clearOpenTimer, clearCloseTimer]);

  const scheduleClose = useCallback((key: string) => {
    clearOpenTimer();
    clearCloseTimer();
    closeTimerRef.current = window.setTimeout(() => {
      setOpenDropdownKey((prev) => (prev === key ? null : prev));
    }, 120);
  }, [clearOpenTimer, clearCloseTimer]);

  const closeDropdown = useCallback(() => setOpenDropdownKey(null), []);

  useEffect(() => {
    return () => {
      clearOpenTimer();
      clearCloseTimer();
    };
  }, [clearOpenTimer, clearCloseTimer]);

  return { openDropdownKey, scheduleOpen, scheduleClose, closeDropdown };
}

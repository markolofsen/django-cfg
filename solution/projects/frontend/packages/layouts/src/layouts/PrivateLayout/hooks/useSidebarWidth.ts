/**
 * Sidebar width: the user drags the edge, the choice is remembered.
 *
 * The width is one CSS variable (`--sidebar-width`) on the provider, so the
 * docked sidebar, its spacer and the peek panel all follow it with no prop
 * plumbing.
 */

'use client';

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { CSSProperties } from 'react';

const STORAGE_KEY = 'cfg.layouts.sidebar-width';
const DEFAULT_WIDTH = 256; // 16rem
const MIN_WIDTH = 224; // 14rem
const MAX_WIDTH = 384; // 24rem

const clamp = (px: number) => Math.min(MAX_WIDTH, Math.max(MIN_WIDTH, Math.round(px)));

function readStored(): number | null {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    const px = raw ? Number(raw) : NaN;
    return Number.isFinite(px) ? clamp(px) : null;
  } catch {
    return null;
  }
}

export interface SidebarWidth {
  enabled: boolean;
  width: number;
  min: number;
  max: number;
  dragging: boolean;
  setWidth: (px: number) => void;
  setDragging: (value: boolean) => void;
  reset: () => void;
  /** CSS variables for the provider element. */
  style: CSSProperties | undefined;
}

export function useSidebarWidth(enabled: boolean): SidebarWidth {
  const [width, setWidthState] = useState(DEFAULT_WIDTH);
  const [dragging, setDragging] = useState(false);

  useEffect(() => {
    if (!enabled) return;
    const stored = readStored();
    if (stored) setWidthState(stored);
  }, [enabled]);

  // Persist once the drag ends, not on every pointer move.
  useEffect(() => {
    if (!enabled || dragging) return;
    try {
      if (width === DEFAULT_WIDTH) window.localStorage.removeItem(STORAGE_KEY);
      else window.localStorage.setItem(STORAGE_KEY, String(width));
    } catch {
      // Storage unavailable: the width simply lasts for the session.
    }
  }, [enabled, dragging, width]);

  const setWidth = useCallback((px: number) => setWidthState(clamp(px)), []);
  const reset = useCallback(() => setWidthState(DEFAULT_WIDTH), []);

  const style = useMemo<CSSProperties | undefined>(
    () => (enabled ? ({ '--sidebar-width': `${width}px` } as CSSProperties) : undefined),
    [enabled, width],
  );

  return useMemo(
    () => ({ enabled, width, min: MIN_WIDTH, max: MAX_WIDTH, dragging, setWidth, setDragging, reset, style }),
    [enabled, width, dragging, setWidth, reset, style],
  );
}

export const SidebarWidthContext = createContext<SidebarWidth | null>(null);

export function useSidebarWidthContext(): SidebarWidth | null {
  return useContext(SidebarWidthContext);
}

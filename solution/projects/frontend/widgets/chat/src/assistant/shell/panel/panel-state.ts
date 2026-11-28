import { useEffect, useSyncExternalStore } from 'react';
import { create } from 'zustand';

/** Where the open flag and the width are remembered. The host decides the keys; reads and writes must never throw. */
export interface UiStorage {
  read: (field: 'open' | 'width') => string | null;
  write: (field: 'open' | 'width', value: string) => void;
}

export interface UiOptions {
  storage?: UiStorage;
  minWidth?: number;
  maxWidth?: number;
  defaultWidth?: number;
  /** Whether the column starts open for a viewer who has never chosen. A choice, once made, is remembered. */
  defaultOpen?: boolean;
  /**
   * The narrowest window (px) where a remembered "open" is restored at page load when `restore` gets no `canOpen` of its own (1280, the usual `dockFrom`). Below it the chat starts closed:
   * a floating window or a full-screen sheet that comes back by itself after every reload covers the page. A choice made in a narrow window is still remembered.
   */
  restoreFrom?: number;
}

export interface UiState {
  open: boolean;
  width: number;
  setOpen: (open: boolean) => void;
  setWidth: (width: number) => void;
  /** Read the remembered state once (`canOpen` decides whether a remembered "open" applies on this screen: a column does, a full-screen sheet must not reopen by itself), once the browser is up (the server render and the first client render both show it closed). */
  restore: (canOpen?: () => boolean) => void;
}

/** Open/closed and column width of the assistant, remembered through `storage`. One store per host app. */
export function createAssistantUi({ storage, minWidth = 320, maxWidth = 560, defaultWidth = 400, defaultOpen = false, restoreFrom = 1280 }: UiOptions = {}) {
  const fits = () => typeof window === 'undefined' || window.innerWidth >= restoreFrom;
  const clamp = (width: number) => Math.min(maxWidth, Math.max(minWidth, Math.round(width)));
  const useUi = create<UiState>((set) => ({
    open: false,
    width: defaultWidth,
    setOpen: (open) => {
      storage?.write('open', open ? '1' : '0');
      set({ open });
    },
    setWidth: (next) => {
      const width = clamp(next);
      storage?.write('width', String(width));
      set({ width });
    },
    restore: (canOpen) => {
      const width = Number(storage?.read('width'));
      const stored = storage?.read('open');
      const wanted = stored == null ? defaultOpen : stored === '1';
      set({ open: wanted && (canOpen ? canOpen() : fits()), width: Number.isFinite(width) && width > 0 ? clamp(width) : defaultWidth });
    },
  }));
  return {
    useUi,
    open: () => useUi.getState().setOpen(true),
    close: () => useUi.getState().setOpen(false),
    limits: { minWidth, maxWidth, defaultWidth },
    /** Mount once in the shell. */
    useRestore: (canOpen?: () => boolean) => {
      const restore = useUi((s) => s.restore);
      useEffect(() => restore(canOpen), []); // eslint-disable-line react-hooks/exhaustive-deps
    },
  };
}

/** A media query as state: `false` on the server and during hydration, so server and first client render agree. */
export function useMediaQuery(query: string): boolean {
  return useSyncExternalStore(
    (onChange) => {
      const list = window.matchMedia(query);
      list.addEventListener('change', onChange);
      return () => list.removeEventListener('change', onChange);
    },
    () => window.matchMedia(query).matches,
    () => false,
  );
}

/** The window's inner width in px as state: `0` on the server and during hydration, so server and first client render agree. */
export function useViewportWidth(): number {
  return useSyncExternalStore(
    (onChange) => {
      window.addEventListener('resize', onChange);
      return () => window.removeEventListener('resize', onChange);
    },
    () => window.innerWidth,
    () => 0,
  );
}

/**
 * The widest the column may be in a window `viewport` px wide: the host's cap, or less when the page must keep `stageMin` px (never below `minWidth`).
 * Without `stageMin`, or before the window width is known (`0`), the cap alone.
 */
export function columnLimit({ minWidth, maxWidth, viewport, stageMin }: { minWidth: number; maxWidth: number; viewport: number; stageMin?: number }): number {
  if (!stageMin || !viewport) return maxWidth;
  return Math.max(minWidth, Math.min(maxWidth, viewport - stageMin));
}

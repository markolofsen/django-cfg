/**
 * Peek: while the sidebar is collapsed, resting the pointer on the left edge or the trigger
 * zone (hover intent) floats the full sidebar over the page. The panel keeps itself open while the pointer is
 * on it, or while a menu opened from it (account, workspace switcher) is open.
 */

'use client';

import React, { createContext, useContext, useEffect, useMemo } from 'react';

import { useSidebar } from '@djangocfg/ui-core/components';
import { useMediaQuery } from '@djangocfg/ui-core/hooks';

import { useHoverIntent } from './useHoverIntent';
import type { Presence } from './usePresence';
import { usePresence } from './usePresence';

type PointerHandlers = ReturnType<typeof useHoverIntent>['zoneProps'];

export interface SidebarPeek extends Presence {
  /** True while the sidebar is collapsed on desktop: the left-edge hot zone is mounted. */
  enabled: boolean;
  /** Hover-open is live: collapsed, desktop, and a fine (mouse/pen) pointer. */
  hoverEnabled: boolean;
  open: boolean;
  zoneProps: PointerHandlers;
  panelProps: PointerHandlers;
  close: () => void;
  /** Keep the panel open while something launched from it is open. */
  pin: (pinned: boolean) => void;
}

const PeekContext = createContext<SidebarPeek | null>(null);

export function useSidebarPeek(): SidebarPeek | null {
  return useContext(PeekContext);
}

/** Pins the peek panel for as long as `active` is true. */
export function usePeekPin(active: boolean): void {
  const peek = useContext(PeekContext);
  const pin = peek?.pin;
  useEffect(() => {
    if (!pin) return;
    pin(active);
    return () => pin(false);
  }, [pin, active]);
}

interface SidebarPeekProviderProps {
  pathname: string;
  children: React.ReactNode;
}

export function SidebarPeekProvider({ pathname, children }: SidebarPeekProviderProps) {
  const { state, isMobile } = useSidebar();
  const enabled = !isMobile && state === 'collapsed';
  // Hover is a mouse affordance: only where the primary pointer can hover precisely.
  const finePointer = useMediaQuery('(hover: hover) and (pointer: fine)');
  const hoverEnabled = enabled && finePointer;

  const intent = useHoverIntent({ enabled: hoverEnabled });
  const { close } = intent;
  const open = enabled && intent.open;
  const presence = usePresence(open);

  useEffect(() => {
    close();
  }, [pathname, close]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') close();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, close]);

  const value = useMemo<SidebarPeek>(
    () => ({
      enabled,
      hoverEnabled,
      open,
      mounted: enabled && presence.mounted,
      state: presence.state,
      zoneProps: intent.zoneProps,
      panelProps: intent.panelProps,
      close,
      pin: intent.pin,
    }),
    [enabled, hoverEnabled, open, presence.mounted, presence.state, intent.zoneProps, intent.panelProps, close, intent.pin],
  );

  return <PeekContext.Provider value={value}>{children}</PeekContext.Provider>;
}

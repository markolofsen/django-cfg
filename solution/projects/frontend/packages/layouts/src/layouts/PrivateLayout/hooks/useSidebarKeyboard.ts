/**
 * Sidebar focus navigation (ArrowUp/Down, Home, End between focusable rows).
 * Cmd/Ctrl+B belongs to `SidebarProvider`; the mobile drawer closes itself on Escape.
 */

'use client';

import { useCallback, useRef } from 'react';

const FOCUSABLE_SELECTOR = [
  'a[href]',
  'button:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(', ');

export function useSidebarKeyboard() {
  const sidebarRef = useRef<HTMLElement | null>(null);

  const handleSidebarKeyDown = useCallback((e: React.KeyboardEvent<HTMLElement>) => {
    const root = sidebarRef.current;
    if (!root) return;

    const focusables = Array.from(root.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR)).filter(
      (el) => el.offsetParent !== null,
    );
    const current = focusables.indexOf(document.activeElement as HTMLElement);
    if (current === -1) return;

    let next: number;
    switch (e.key) {
      case 'ArrowDown':
        next = (current + 1) % focusables.length;
        break;
      case 'ArrowUp':
        next = (current - 1 + focusables.length) % focusables.length;
        break;
      case 'Home':
        next = 0;
        break;
      case 'End':
        next = focusables.length - 1;
        break;
      default:
        return;
    }
    e.preventDefault();
    focusables[next]?.focus();
  }, []);

  const setSidebarRef = useCallback((node: HTMLElement | null) => {
    sidebarRef.current = node;
  }, []);

  return { setSidebarRef, handleSidebarKeyDown };
}

'use client';

import { useEffect, useRef, useState } from 'react';

/** Slightly above `transition-[transform,opacity] duration-[220ms]` in PublicMobileDrawer */
const CLOSE_UNMOUNT_MS = 230;

/**
 * Keeps the mobile nav panel mounted briefly after `isOpen` becomes false so CSS can run the close transition,
 * then unmounts — no reliance on `transitionend` (fragile with SPA navigation / Safari).
 */
export function useMobileNavPanel(options: { isOpen: boolean; onClose: () => void }) {
  const { isOpen, onClose } = options;
  const [mounted, setMounted] = useState(isOpen);
  const [visible, setVisible] = useState(isOpen);
  const closeTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (isOpen) {
      if (closeTimerRef.current) {
        clearTimeout(closeTimerRef.current);
        closeTimerRef.current = null;
      }
      setMounted(true);
      const id = requestAnimationFrame(() => {
        requestAnimationFrame(() => setVisible(true));
      });
      return () => cancelAnimationFrame(id);
    }

    setVisible(false);
    closeTimerRef.current = setTimeout(() => {
      setMounted((m) => (m ? false : m));
      closeTimerRef.current = null;
    }, CLOSE_UNMOUNT_MS);

    return () => {
      if (closeTimerRef.current) {
        clearTimeout(closeTimerRef.current);
        closeTimerRef.current = null;
      }
    };
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [isOpen, onClose]);

  return { mounted, visible };
}

/**
 * Mobile Overlay Component
 * Backdrop overlay for mobile sidebar
 */

'use client';

import React from 'react';
import { cn } from '@djangocfg/ui/lib';
import { useIsMobile } from '@djangocfg/ui';

interface MobileOverlayProps {
  isOpen: boolean;
  onClose: () => void;
}

export function MobileOverlay({ isOpen, onClose }: MobileOverlayProps) {
  const isMobile = useIsMobile();

  // Only show on mobile when sidebar is open
  if (!isMobile || !isOpen) return null;

  return (
    <div
      className={cn(
        "fixed inset-0 z-[150] bg-background/80 backdrop-blur-sm",
        "animate-in fade-in duration-300"
      )}
      onClick={onClose}
      aria-hidden="true"
    />
  );
}

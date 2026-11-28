'use client';

import React from 'react';
import { createPortal } from 'react-dom';

import { portalPopoverCls } from './navDesktopStyles';

export function DesktopDropdownPortal({
  anchor,
  children,
  onMouseEnter,
  onMouseLeave,
}: {
  anchor: HTMLElement;
  children: React.ReactNode;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
}) {
  const [position, setPosition] = React.useState({ left: 0, top: 0 });

  React.useLayoutEffect(() => {
    const updatePosition = () => {
      const rect = anchor.getBoundingClientRect();
      setPosition({ left: rect.left, top: rect.bottom + 4 });
    };

    updatePosition();
    window.addEventListener('resize', updatePosition);
    window.addEventListener('scroll', updatePosition, true);
    return () => {
      window.removeEventListener('resize', updatePosition);
      window.removeEventListener('scroll', updatePosition, true);
    };
  }, [anchor]);

  return createPortal(
    <div
      className={portalPopoverCls}
      style={position}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
    >
      {children}
    </div>,
    document.body,
  );
}

/**
 * Drag handle on the sidebar's right edge. Pointer drag, arrow keys and
 * double-click-to-reset; the width itself lives in `useSidebarWidth`.
 */

'use client';

import React, { useRef } from 'react';

import { useSidebarWidthContext } from '../hooks';

const KEY_STEP = 16;

export function SidebarResizeHandle() {
  const sidebarWidth = useSidebarWidthContext();
  const origin = useRef<{ x: number; width: number } | null>(null);

  if (!sidebarWidth?.enabled) return null;
  const { width, min, max, dragging, setWidth, setDragging, reset } = sidebarWidth;

  const onPointerDown = (e: React.PointerEvent<HTMLDivElement>) => {
    if (e.button !== 0) return;
    e.currentTarget.setPointerCapture(e.pointerId);
    origin.current = { x: e.clientX, width };
    setDragging(true);
  };

  const onPointerMove = (e: React.PointerEvent<HTMLDivElement>) => {
    if (!origin.current) return;
    setWidth(origin.current.width + e.clientX - origin.current.x);
  };

  const endDrag = () => {
    origin.current = null;
    setDragging(false);
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    const next =
      e.key === 'ArrowLeft' ? width - KEY_STEP
      : e.key === 'ArrowRight' ? width + KEY_STEP
      : e.key === 'Home' ? min
      : e.key === 'End' ? max
      : null;
    if (next === null) return;
    e.preventDefault();
    e.stopPropagation();
    setWidth(next);
  };

  return (
    <div
      role="separator"
      aria-orientation="vertical"
      aria-label="Resize sidebar"
      aria-valuemin={min}
      aria-valuemax={max}
      aria-valuenow={width}
      tabIndex={0}
      data-dragging={dragging || undefined}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={endDrag}
      onPointerCancel={endDrag}
      onDoubleClick={reset}
      onKeyDown={onKeyDown}
      className={[
        'absolute inset-y-0 right-0 z-20 hidden w-2 cursor-col-resize touch-none outline-none md:block',
        // 2px primary line on the border; fades in after a short hover delay.
        'after:absolute after:inset-y-0 after:-right-px after:w-[2px] after:bg-transparent',
        'after:transition-colors after:duration-150',
        'hover:after:bg-primary hover:after:delay-100 focus-visible:after:bg-primary data-[dragging]:after:bg-primary',
      ].join(' ')}
    />
  );
}

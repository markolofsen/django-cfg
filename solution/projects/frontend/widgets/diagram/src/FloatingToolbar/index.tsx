'use client';

import React, { useEffect, useState } from 'react';

import './FloatingToolbar.css';
import { useScrollIsolation } from './hooks/useScrollIsolation';

/**
 * Track whether the container actually overflows. Scroll isolation
 * (and its "Click to scroll" overlay) only makes sense when there is
 * something to scroll — a fully-visible block must stay interactive.
 */
function useIsScrollable(ref: React.RefObject<HTMLElement | null>): boolean {
  const [scrollable, setScrollable] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const measure = () => {
      // 1px tolerance for sub-pixel rounding.
      setScrollable(
        el.scrollHeight - el.clientHeight > 1 ||
          el.scrollWidth - el.clientWidth > 1,
      );
    };

    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(el);
    return () => observer.disconnect();
  }, [ref]);

  return scrollable;
}

export interface FloatingToolbarProps {
  /** Ref to the container element the toolbar anchors to */
  containerRef: React.RefObject<HTMLElement | null>;
  /** Action buttons to render (right side) */
  children: React.ReactNode;
  /** Optional label shown left of the buttons (e.g. language badge) */
  label?: React.ReactNode;
  /** Where to anchor relative to the container (default: bottom-right) */
  position?: 'top-right' | 'bottom-right';
  /** Offset from the edge in px (default: 8) */
  offset?: number;
  /** z-index (default: 30) */
  zIndex?: number;
  /**
   * Block wheel scroll inside the container until user clicks into it.
   * Re-locks when mouse leaves. Like Google Maps scroll isolation.
   * @default true
   */
  scrollIsolation?: boolean;
  /**
   * Hide the toolbar until the user hovers the container. ChatGPT /
   * GitHub-style: chrome stays out of the way, appears on demand.
   * Keyboard focus inside the container also reveals it (a11y).
   * @default false (always visible — back-compat)
   */
  autoHide?: boolean;
}

/**
 * Toolbar is anchored with `position: absolute` inside the container (PrettyCode, etc.).
 * `position: fixed` + viewport coordinates breaks embedded layouts (e.g. chat composer overlap).
 */
export const FloatingToolbar: React.FC<FloatingToolbarProps> = ({
  containerRef,
  children,
  label,
  position = 'bottom-right',
  offset = 8,
  zIndex = 30,
  scrollIsolation = true,
  autoHide = false,
}) => {
  // Isolation only engages when the container can actually scroll —
  // a block that fully fits never shows the "Click to scroll" overlay.
  const isScrollable = useIsScrollable(containerRef);
  const isolationActive = scrollIsolation && isScrollable;

  const { locked, unlock } = useScrollIsolation(containerRef, isolationActive);
  const [overlayHovered, setOverlayHovered] = useState(false);

  // Track container hover + focus for ChatGPT-style auto-hide. We watch
  // `mouseenter/leave` and `focusin/out` on the container so keyboard
  // users still see the toolbar — `:hover` alone would hide it from
  // them entirely.
  const [containerActive, setContainerActive] = useState(false);
  useEffect(() => {
    if (!autoHide) return;
    const el = containerRef.current;
    if (!el) return;
    const enter = () => setContainerActive(true);
    const leave = () => setContainerActive(false);
    el.addEventListener('mouseenter', enter);
    el.addEventListener('mouseleave', leave);
    el.addEventListener('focusin', enter);
    el.addEventListener('focusout', leave);
    return () => {
      el.removeEventListener('mouseenter', enter);
      el.removeEventListener('mouseleave', leave);
      el.removeEventListener('focusin', enter);
      el.removeEventListener('focusout', leave);
    };
  }, [autoHide, containerRef]);

  const overlay =
    isolationActive && locked ? (
      <div
        onClick={unlock}
        onMouseEnter={() => setOverlayHovered(true)}
        onMouseLeave={() => setOverlayHovered(false)}
        style={{
          position: 'absolute',
          inset: 0,
          zIndex: zIndex - 1,
          cursor: 'pointer',
          background: overlayHovered ? 'rgba(0,0,0,0.04)' : 'transparent',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'background 150ms',
        }}
      >
        {overlayHovered && (
          <span
            style={{
              fontSize: '0.75rem',
              padding: '0.25rem 0.625rem',
              borderRadius: '9999px',
              background: 'rgba(0,0,0,0.55)',
              color: '#fff',
              pointerEvents: 'none',
              userSelect: 'none',
            }}
          >
            Click to scroll
          </span>
        )}
      </div>
    ) : null;

  const positionStyle: React.CSSProperties =
    position === 'bottom-right'
      ? { bottom: offset, right: offset }
      : { top: offset, right: offset };

  // Auto-hide: invisible until the container is hovered or has keyboard
  // focus inside. Opacity transition keeps the reveal smooth instead of
  // popping. `pointer-events: none` while hidden so the toolbar doesn't
  // intercept clicks on whatever sits behind it.
  const hidden = autoHide && !containerActive;
  const toolbar = (
    <div
      className="flex items-center gap-1"
      style={{
        position: 'absolute',
        ...positionStyle,
        zIndex,
        opacity: hidden ? 0 : 1,
        pointerEvents: hidden ? 'none' : undefined,
        transition: 'opacity 120ms ease-out',
      }}
    >
      {label && (
        <>
          {label}
          <div className="w-px h-4 bg-border/50 mx-0.5" />
        </>
      )}
      {children}
    </div>
  );

  return (
    <>
      {overlay}
      {toolbar}
    </>
  );
};

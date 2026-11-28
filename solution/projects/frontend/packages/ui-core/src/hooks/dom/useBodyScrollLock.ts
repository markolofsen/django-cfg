'use client';

import { useEffect, useRef } from 'react';

import { useDeviceDetect } from '../device/useDeviceDetect';

/**
 * useBodyScrollLock — locks body scroll while `locked` is true.
 *
 * Safe to use from multiple components concurrently: a module-scope counter
 * tracks active locks and only releases the lock when the last caller unmounts
 * (or passes `locked=false`).
 *
 * Strategy:
 *  - iOS Safari: pin body in place with `position: fixed; top: -scrollY` and
 *    restore scroll on release. `overflow: hidden` alone is ignored on iOS.
 *  - Other browsers: `body.overflow = 'hidden'` plus a `paddingRight`
 *    compensator for the disappearing scrollbar so layout doesn't shift.
 *    We intentionally do NOT touch `html.overflow` — that removes the
 *    scrolling container for `position: sticky` descendants and breaks
 *    sticky navbars while the lock is active.
 *
 * @example
 * useBodyScrollLock(isMobile && drawerOpen);
 */

let lockCount = 0;
interface SavedState {
  bodyOverflow: string;
  bodyPaddingRight: string;
  bodyPosition: string;
  bodyTop: string;
  bodyWidth: string;
  scrollY: number;
  iosMode: boolean;
}
let saved: SavedState | null = null;

function getScrollbarWidth(): number {
  if (typeof window === 'undefined') return 0;
  return window.innerWidth - document.documentElement.clientWidth;
}

function applyLock(iosMode: boolean) {
  const body = document.body;
  const scrollY = window.scrollY;

  saved = {
    bodyOverflow: body.style.overflow,
    bodyPaddingRight: body.style.paddingRight,
    bodyPosition: body.style.position,
    bodyTop: body.style.top,
    bodyWidth: body.style.width,
    scrollY,
    iosMode,
  };

  if (iosMode) {
    // iOS Safari ignores `overflow: hidden` on body — pin body in place and
    // remember scroll position so we can restore it on release.
    body.style.position = 'fixed';
    body.style.top = `-${scrollY}px`;
    body.style.width = '100%';
    body.style.overflow = 'hidden';
  } else {
    // Avoid touching `html.overflow`: it breaks `position: sticky` ancestors
    // (they lose their scrolling container and fall back to static flow).
    const scrollbarWidth = getScrollbarWidth();
    if (scrollbarWidth > 0) {
      const current = parseFloat(window.getComputedStyle(body).paddingRight) || 0;
      body.style.paddingRight = `${current + scrollbarWidth}px`;
    }
    body.style.overflow = 'hidden';
  }
}

function releaseLock() {
  if (!saved) return;
  const body = document.body;
  const { iosMode, scrollY } = saved;

  body.style.overflow = saved.bodyOverflow;
  body.style.paddingRight = saved.bodyPaddingRight;
  body.style.position = saved.bodyPosition;
  body.style.top = saved.bodyTop;
  body.style.width = saved.bodyWidth;

  if (iosMode) {
    window.scrollTo(0, scrollY);
  }

  saved = null;
}

export function useBodyScrollLock(locked: boolean): void {
  const device = useDeviceDetect();

  // `isIOS` starts false and flips once the UA parse resolves. With it in the
  // deps the effect re-ran on that flip: the cleanup dropped the shared
  // lockCount to 0 and released the lock — unlocking the page under a second
  // overlay that was still open. The lock strategy is chosen once, on the
  // acquisition that takes the count from 0 to 1.
  const isIOSRef = useRef(device.isIOS);
  isIOSRef.current = device.isIOS;

  useEffect(() => {
    if (!locked) return;
    if (typeof document === 'undefined') return;

    if (lockCount === 0) {
      applyLock(isIOSRef.current);
    }
    lockCount += 1;

    return () => {
      lockCount = Math.max(0, lockCount - 1);
      if (lockCount === 0) {
        releaseLock();
      }
    };
  }, [locked]);
}

'use client';

import { useEffect, useRef, useState, type RefObject } from 'react';

import { useScroll } from '@djangocfg/ui-core/hooks';

export interface UseNavbarScrollOptions {
  /** Slide navbar up on scroll-down, back on scroll-up. @default false */
  hideNavOnScroll?: boolean;
  /** Transparent at page top, opaque after threshold. @default false */
  transparent?: boolean;
  /** scrollY threshold for hide + transparent triggers. @default 40 */
  transparentThreshold?: number;
  /** Scroll container to follow instead of the window (shells where the document never scrolls). */
  target?: RefObject<HTMLElement | null>;
  /** When false the hide still happens under `prefers-reduced-motion` (the caller drops the animation). @default true */
  respectReducedMotion?: boolean;
}

export interface UseNavbarScrollReturn {
  /** true → apply `-translate-y-full` to outer wrapper */
  hidden: boolean;
  /** true → scrollY >= threshold; drives opaque background */
  scrolled: boolean;
}

/**
 * How much accumulated movement in one direction it takes to flip the navbar.
 *
 * The whole point: react to *intent*, not to every pixel. A raw
 * `direction === 'down' → hide` flickers on a trackpad's jittery micro-scrolls
 * and on Safari's momentum tail, where the delta's sign wobbles frame to frame.
 * We integrate movement instead and only commit once it clears this gate, then
 * reset — so one deliberate flick hides, but noise around zero does nothing.
 */
const DIRECTION_COMMIT_PX = 8;

/**
 * Navbar scroll behaviour, built on ui-core's shared `useScroll` store.
 *
 * We deliberately do NOT attach our own scroll listener: `useScroll` already
 * runs a single rAF-throttled, `useSyncExternalStore`-backed listener per
 * target for the whole page (its own JSDoc points at this hook as the intended
 * consumer — "for cumulative direction, build on top of this"). Here we add the
 * navbar-specific *policy* on top of that raw position:
 *
 *   - a commit threshold so micro-scroll / momentum jitter can't flip the bar
 *   - overscroll clamping so Safari rubber-banding at the edges doesn't twitch
 *   - "always visible near the top" and "don't hide if there's nothing to
 *     reclaim"
 *   - `prefers-reduced-motion` opt-out of the hide (the slide, not the fade)
 *
 * All of that lives in refs and only touches React state when the derived
 * boolean actually flips, so a page of scrolling costs at most a couple of
 * renders.
 */
export function useNavbarScroll(options: UseNavbarScrollOptions = {}): UseNavbarScrollReturn {
  const { hideNavOnScroll = false, transparent = false, transparentThreshold = 40, target, respectReducedMotion = true } = options;

  const active = hideNavOnScroll || transparent;
  // Subscribe to the shared store only when the feature is on. The `y` this
  // returns is already rAF-coalesced; we run cheap arithmetic on each change.
  const { y } = useScroll(active ? target : NEVER_TARGET);

  const [hidden, setHidden] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  // Cumulative-direction state — refs so integrating never forces a render.
  const lastY = useRef(0);
  const accum = useRef(0);
  const hiddenRef = useRef(false);
  const scrolledRef = useRef(false);

  useEffect(() => {
    if (!active) {
      // Feature off → make sure we don't leave the bar stuck hidden/opaque.
      hiddenRef.current = false;
      scrolledRef.current = false;
      accum.current = 0;
      setHidden(false);
      setScrolled(false);
      return;
    }

    // Respect the user's motion preference: if they've asked for reduced
    // motion, never yank the bar out of view — it can be disorienting. The
    // transparency fade (opacity, not a translate) is still fine.
    const prefersReducedMotion =
      typeof window.matchMedia === 'function' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const hideEnabled = hideNavOnScroll && !(respectReducedMotion && prefersReducedMotion);

    // iOS Safari rubber-banding reports negative scrollY at the top and values
    // past maxScroll at the bottom while the page bounces back; feeding those
    // into the integrator makes the bar twitch on every overscroll pull.
    const el = target?.current;
    const maxScroll = el
      ? Math.max(0, el.scrollHeight - el.clientHeight)
      : Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    const clampedY = Math.min(Math.max(0, y), maxScroll);

    if (transparent) {
      const next = clampedY >= transparentThreshold;
      if (scrolledRef.current !== next) {
        scrolledRef.current = next;
        setScrolled(next);
      }
    }

    if (hideEnabled) {
      // Near the top there's nowhere to hide *to*, and the header is usually
      // part of the hero — always show. Same when the page can't scroll a full
      // viewport (nothing to reclaim by hiding).
      if (clampedY <= transparentThreshold || maxScroll <= 0) {
        accum.current = 0;
        if (hiddenRef.current) {
          hiddenRef.current = false;
          setHidden(false);
        }
      } else {
        const delta = clampedY - lastY.current;
        // Reset the integrator whenever direction reverses, so a flick the
        // other way takes full effect immediately instead of first paying off
        // the debt built up going the previous way.
        if ((delta > 0 && accum.current < 0) || (delta < 0 && accum.current > 0)) {
          accum.current = 0;
        }
        accum.current += delta;

        if (accum.current >= DIRECTION_COMMIT_PX && !hiddenRef.current) {
          hiddenRef.current = true;
          setHidden(true);
          accum.current = 0;
        } else if (accum.current <= -DIRECTION_COMMIT_PX && hiddenRef.current) {
          hiddenRef.current = false;
          setHidden(false);
          accum.current = 0;
        }
      }
    }

    lastY.current = clampedY;
  }, [y, active, hideNavOnScroll, transparent, transparentThreshold, target, respectReducedMotion]);

  return { hidden, scrolled };
}

/**
 * A stable ref target whose `.current` is always null, so `useScroll` resolves
 * to "no target" and never subscribes when the feature is off. Module-level so
 * its identity is stable across renders (a fresh object each render would make
 * `useScroll`'s `useCallback` deps churn).
 */
const NEVER_TARGET = { current: null } as const;

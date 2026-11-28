'use client';

import { type RefObject, useEffect } from 'react';

/**
 * Measures navbar geometry into CSS custom properties on `:root` so the rest of
 * the page can lay itself out against the real bar — without prop-drilling a
 * pixel number through React or hardcoding a magic height.
 *
 * Writes:
 *   --public-navbar-height              the bar's own rendered height (px)
 *   --public-navbar-mobile-drawer-top   y where the mobile drawer should start
 *   --public-navbar-mobile-drawer-max-height
 *   --dvh                               1% of the *stable* visual-viewport height
 *
 * Why `--dvh` and not just the CSS `dvh` unit: a length written in `dvh` with a
 * CSS transition on it re-animates on every step of the mobile browser chrome
 * collapsing/expanding — a jittery, stuttering result. This var is updated from
 * `visualViewport` only on real resize (chrome settled), so heights built on
 * `calc(var(--dvh) * 100)` stay smooth. Sections that don't animate can keep
 * using the native `dvh` unit directly.
 *
 * @param navOuterRef - ref on the outermost navbar wrapper div
 * @param deps        - values that should re-trigger observer setup (position, variant, containerClassName)
 */
export function useNavbarViewportVars(
  navOuterRef: RefObject<HTMLDivElement | null>,
  deps: readonly unknown[],
): void {
  useEffect(() => {
    const root = document.documentElement;
    const vv = window.visualViewport;

    // Navbar height + the mobile-drawer anchoring. Depends on the navbar's own
    // box, so it belongs on the ResizeObserver + scroll path (a hide-on-scroll
    // bar's `rect.bottom` moves as it slides).
    const updateNav = () => {
      const navEl = navOuterRef.current;
      if (!navEl) return;

      const rect = navEl.getBoundingClientRect();

      // The bar's intrinsic height (not affected by a hide translate — that's
      // why we read `height`, not `bottom - top` off a possibly-translated
      // box). offsetHeight is layout height, stable across the slide.
      const navHeight = Math.round(navEl.offsetHeight);
      root.style.setProperty('--public-navbar-height', `${navHeight}px`);

      const top = Math.max(0, Math.round(rect.bottom + 8));
      const maxHeight = Math.max(240, window.innerHeight - top - 12);
      root.style.setProperty('--public-navbar-mobile-drawer-top', `${top}px`);
      root.style.setProperty('--public-navbar-mobile-drawer-max-height', `${maxHeight}px`);
    };

    // Stable viewport-height unit. `visualViewport.height` excludes the mobile
    // browser chrome and (with `interactive-widget=resizes-content`) the
    // on-screen keyboard, which is exactly what we want a full-height section
    // to fit into. Updated only on resize so animated heights don't stutter.
    const updateDvh = () => {
      const h = vv?.height ?? window.innerHeight;
      root.style.setProperty('--dvh', `${h / 100}px`);
    };

    updateNav();
    updateDvh();

    const navEl = navOuterRef.current;
    const observer = navEl ? new ResizeObserver(updateNav) : null;
    if (navEl && observer) observer.observe(navEl);

    // Nav geometry tracks scroll (the bar slides) + window resize.
    window.addEventListener('resize', updateNav);
    window.addEventListener('scroll', updateNav, { passive: true });

    // `--dvh` intentionally does NOT listen to scroll: reacting to the mobile
    // chrome mid-collapse is the jitter we're avoiding. Only settled resizes.
    window.addEventListener('resize', updateDvh);
    vv?.addEventListener('resize', updateDvh);

    return () => {
      if (navEl && observer) observer.unobserve(navEl);
      observer?.disconnect();
      window.removeEventListener('resize', updateNav);
      window.removeEventListener('scroll', updateNav);
      window.removeEventListener('resize', updateDvh);
      vv?.removeEventListener('resize', updateDvh);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
}

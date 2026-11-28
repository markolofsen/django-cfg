'use client';

import { useEffect, useState } from 'react';

import { resolveRefs, type RefResolver } from './resolve-ref';
import type { HighlightTarget, PointDirective } from './types';
import { waitForVisible } from './wait-for-visible';

/** Is a rect fully inside the viewport. */
function isOnScreen(rect: DOMRect): boolean {
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <= window.innerHeight &&
    rect.right <= window.innerWidth
  );
}

/**
 * Resolve `point` directives into live, geometry-tracked highlight
 * targets.
 *
 * - resolves each ref to a DOM element (drops stale ones);
 * - scrolls an off-screen target into view and waits until it is
 *   actually visible before exposing it — so the spotlight is drawn at
 *   the element's settled position, never mid-scroll;
 * - measures rects and keeps them fresh on scroll / resize;
 * - moves focus into a target when the directive asked for it;
 * - drops a target automatically if its element leaves the DOM.
 *
 * One effect owns the whole lifecycle — resolve, side-effects, and the
 * geometry subscription — so there is no ordering ambiguity between
 * separate effects.
 */
export function useHighlightTargets(
  directives: PointDirective[],
  resolver: RefResolver | null,
): HighlightTarget[] {
  const [targets, setTargets] = useState<HighlightTarget[]>([]);

  useEffect(() => {
    // Resolve every directive that wants a highlight to a live element.
    const wanted = directives.filter((d) => d.highlight !== false);
    const resolved = resolveRefs(
      wanted.map((d) => d.ref),
      resolver,
    );
    const pairs = resolved
      .map(({ ref, element }) => {
        const directive = wanted.find((d) => d.ref === ref);
        return directive ? { element, directive } : null;
      })
      .filter(
        (p): p is { element: HTMLElement; directive: PointDirective } =>
          p !== null,
      );

    if (pairs.length === 0) {
      setTargets([]);
      return;
    }

    let cancelled = false;

    // A pair is only drawn once `ready` is true. Already-visible
    // targets are ready immediately; off-screen ones become ready
    // after their scroll-into-view settles (or its safety timeout).
    const ready = new WeakSet<HTMLElement>();

    // Measure all *ready* targets — called now and on every
    // scroll / resize. Off-screen-but-not-yet-settled targets are
    // skipped so their spotlight is never drawn at a stale position.
    const measure = () => {
      const next: HighlightTarget[] = [];
      for (const { element, directive } of pairs) {
        if (!element.isConnected) continue; // element left the DOM
        if (!ready.has(element)) continue; // still scrolling into view
        next.push({
          element,
          rect: element.getBoundingClientRect(),
          label: directive.label,
          focus: directive.focus ?? false,
        });
      }
      setTargets(next);
    };

    let frame = 0;
    const schedule = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(measure);
    };

    // Split targets into the ones already on screen and the ones that
    // need to be scrolled into view first.
    const offScreen: HTMLElement[] = [];
    for (const { element } of pairs) {
      if (isOnScreen(element.getBoundingClientRect())) {
        ready.add(element);
      } else {
        offScreen.push(element);
      }
    }

    // Scroll each off-screen target into view, then wait until it is
    // actually visible before marking it ready and re-measuring.
    for (const element of offScreen) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      void waitForVisible(element).then(() => {
        if (cancelled || !element.isConnected) return;
        ready.add(element);
        schedule();
      });
    }

    // Focus a target if requested — after its scroll-into-view settles
    // so focus() does not fight the smooth scroll.
    const focusPair = pairs.find((p) => p.directive.focus);
    if (focusPair) {
      const el = focusPair.element;
      const applyFocus = () => {
        if (cancelled || !el.isConnected) return;
        // Make a non-focusable element focusable so focus() lands.
        const nativelyFocusable = [
          'INPUT',
          'TEXTAREA',
          'SELECT',
          'BUTTON',
          'A',
        ].includes(el.tagName);
        if (el.tabIndex < 0 && !nativelyFocusable) el.tabIndex = -1;
        el.focus({ preventScroll: true });
      };
      if (isOnScreen(el.getBoundingClientRect())) {
        applyFocus();
      } else {
        void waitForVisible(el).then(applyFocus);
      }
    }

    // Initial measure (draws any already-visible targets) + keep
    // geometry fresh.
    measure();
    window.addEventListener('scroll', schedule, true);
    window.addEventListener('resize', schedule);
    const observer = new ResizeObserver(schedule);
    for (const { element } of pairs) observer.observe(element);

    return () => {
      cancelled = true;
      cancelAnimationFrame(frame);
      window.removeEventListener('scroll', schedule, true);
      window.removeEventListener('resize', schedule);
      observer.disconnect();
    };
  }, [directives, resolver]);

  return targets;
}

/**
 * useResponsiveOverflow — figure out how many nav items fit in the available
 * space, pushing the rest into a "More" dropdown.
 *
 * Strategy (SSR-safe, no flash):
 *  1. On the server and first client render we return `count === total`; the
 *     caller renders every item inside an *invisible* measurement layer plus
 *     the live row (see caller). No layout is committed until the observer
 *     runs.
 *  2. After mount, a ResizeObserver on the container + per-item width reads
 *     recompute `visibleCount` whenever the nav's available width changes.
 *  3. We reserve space for a "More" chip when anything is overflowing, so the
 *     chip itself never pushes the last visible item out (which would cause
 *     thrash: n → n-1 → n → …).
 */

'use client';

import { useCallback, useEffect, useRef, useState, type RefCallback } from 'react';

interface Options {
  total: number;
  /** Approx width reserved for the "More" chip when overflow exists. */
  moreWidth?: number;
  /** Gap between items (must match the flex gap in px). */
  gap?: number;
  /** Min items that must always be visible (clamps lower bound to 1). */
  minVisible?: number;
}

interface Result {
  /** How many items fit. */
  visibleCount: number;
  /** Attach to the container that constrains width. */
  containerRef: RefCallback<HTMLElement | null>;
  /** Attach to each item in the measurement layer (call for every index 0..total-1). */
  itemRef: (index: number) => RefCallback<HTMLElement | null>;
  /** True once a measurement has happened — caller can hide the measure layer then. */
  measured: boolean;
}

export function useResponsiveOverflow({
  total,
  moreWidth = 72,
  gap = 4,
  minVisible = 1,
}: Options): Result {
  const [visibleCount, setVisibleCount] = useState<number>(total);
  const [measured, setMeasured] = useState(false);

  const containerElRef = useRef<HTMLElement | null>(null);
  const itemElsRef = useRef<Array<HTMLElement | null>>([]);
  const roRef = useRef<ResizeObserver | null>(null);

  const recompute = useCallback(() => {
    const container = containerElRef.current;
    if (!container) return;
    const available = container.clientWidth;
    if (available <= 0) return;

    // Built with `from` rather than an index loop so `widths` and `total` cannot
    // disagree on length — the two reads below then need no bounds check.
    const widths = Array.from({ length: total }, (_, i) => {
      const el = itemElsRef.current[i];
      return el ? Math.ceil(el.getBoundingClientRect().width) : 0;
    });

    // Try to fit all first.
    const usedAll = widths.reduce(
      (sum, width, i) => sum + width + (i > 0 ? gap : 0),
      0,
    );
    if (usedAll <= available) {
      setVisibleCount(total);
      setMeasured(true);
      return;
    }

    // Some overflow: reserve space for the "More" chip.
    const budget = available - moreWidth - gap;
    let used = 0;
    let fit = 0;
    // Iterating values, not indices: this loop breaks early, so `reduce` does
    // not fit, and `entries()` still keeps each width tied to its position.
    for (const [i, width] of widths.entries()) {
      const next = used + width + (i > 0 ? gap : 0);
      if (next > budget) break;
      used = next;
      fit = i + 1;
    }

    const clamped = Math.max(minVisible, Math.min(total, fit));
    setVisibleCount(clamped);
    setMeasured(true);
  }, [total, moreWidth, gap, minVisible]);

  // Recompute when `total` changes (items added/removed).
  useEffect(() => {
    itemElsRef.current.length = total;
    recompute();
  }, [total, recompute]);

  const containerRef = useCallback<RefCallback<HTMLElement | null>>(
    (node) => {
      // Tear down previous observer.
      if (roRef.current) {
        roRef.current.disconnect();
        roRef.current = null;
      }
      containerElRef.current = node;
      if (!node) return;
      if (typeof ResizeObserver === 'undefined') {
        recompute();
        return;
      }
      const ro = new ResizeObserver(() => recompute());
      ro.observe(node);
      roRef.current = ro;
      // Initial measurement — rAF to let children mount.
      requestAnimationFrame(recompute);
    },
    [recompute],
  );

  const itemRef = useCallback(
    (index: number): RefCallback<HTMLElement | null> =>
      (node) => {
        itemElsRef.current[index] = node;
      },
    [],
  );

  useEffect(() => {
    return () => {
      if (roRef.current) {
        roRef.current.disconnect();
        roRef.current = null;
      }
    };
  }, []);

  return { visibleCount, containerRef, itemRef, measured };
}

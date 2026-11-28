import { useCallback, useRef, type RefCallback } from "react";

import { boxVars, readViewportBox } from "../../core/screen";

interface TrackOptions {
  /** The keyboard opened or closed. */
  readonly onKeyboard?: (open: boolean) => void;
}

/**
 * Keeps `--vvh`, `--vvw`, `--vv-top`, `--vv-left`, `--kb` and `data-keyboard` of `node` equal to the visible area while the keyboard is up; with it down only `--kb: 0px` stays and CSS sizes the layer from `dvh`.
 *
 * Reads once at once (from the ref callback, before the first paint), then on `visualViewport` resize and scroll and on
 * rotation. The write happens INSIDE the event, not a frame later: iOS pans the visual viewport during the keyboard
 * animation, and a layer that follows one frame late shows the page behind it as a strip. A rotation is read again
 * after it settles, because iOS reports the old size mid-turn. Styles are written directly, so there is no React render
 * per event.
 */
export function trackViewport(node: HTMLElement, { onKeyboard }: TrackOptions = {}): () => void {
  const vv = window.visualViewport;
  if (!vv) return () => {};
  let baseline = vv.height;
  let keyboard = false;
  let settle = 0;

  const apply = () => {
    const box = readViewportBox(vv, window.innerHeight, baseline);
    baseline = Math.max(baseline, box.height);
    // Only a raised keyboard needs the measured box. Without one the CSS fallbacks (`dvh`, top 0) are exact, and the
    // measured numbers are not trustworthy: iOS 26 leaves `offsetTop` stale after the keyboard closes, which pushed the sheet down.
    for (const [name, value] of Object.entries(boxVars(box))) {
      if (box.keyboard || name === "--kb") node.style.setProperty(name, value);
      else node.style.removeProperty(name);
    }
    if (box.keyboard !== keyboard) {
      keyboard = box.keyboard;
      node.toggleAttribute("data-keyboard", keyboard);
      onKeyboard?.(keyboard);
    }
  };
  const rotated = () => {
    baseline = 0;
    apply();
    window.clearTimeout(settle);
    settle = window.setTimeout(() => {
      baseline = vv.height;
      apply();
    }, 250);
  };

  apply();
  vv.addEventListener("resize", apply);
  vv.addEventListener("scroll", apply);
  window.addEventListener("orientationchange", rotated);
  return () => {
    vv.removeEventListener("resize", apply);
    vv.removeEventListener("scroll", apply);
    window.removeEventListener("orientationchange", rotated);
    window.clearTimeout(settle);
  };
}

/** A ref for the layer element: while it is mounted and `enabled`, it carries the box (see `trackViewport`). */
export function useViewportBox<T extends HTMLElement>(
  enabled: boolean,
  onKeyboard?: (open: boolean) => void,
): RefCallback<T> {
  const stop = useRef<(() => void) | null>(null);
  const keyboard = useRef(onKeyboard);
  keyboard.current = onKeyboard;
  return useCallback(
    (node: T | null) => {
      stop.current?.();
      stop.current = null;
      if (node && enabled) stop.current = trackViewport(node, { onKeyboard: (open) => keyboard.current?.(open) });
    },
    [enabled],
  );
}

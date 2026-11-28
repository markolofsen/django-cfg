// The visible area of a phone, as numbers. No DOM: `visualViewport` is read by
// the caller (`primitives/layer/use-viewport-box`) and handed in as plain values, so
// the arithmetic is testable headless.

/** Smallest shrink of the visible area that counts as an on-screen keyboard (a collapsing URL bar is about 100px). */
export const KEYBOARD_MIN = 120;

/** What `window.visualViewport` reports, as plain numbers. */
export interface ViewportSample {
  readonly width: number;
  readonly height: number;
  readonly offsetTop: number;
  readonly offsetLeft: number;
}

export interface ViewportBox {
  /** Visible width in px. */
  readonly width: number;
  /** Visible height in px. */
  readonly height: number;
  /** Distance of the visible area from the top of the layout viewport (iOS pans it when the keyboard opens). */
  readonly top: number;
  readonly left: number;
  /** Keyboard height: the part of the layout viewport the visible area does not cover. */
  readonly kb: number;
  readonly keyboard: boolean;
}

/**
 * Pure reading of `visualViewport`.
 *
 * iOS keeps the layout viewport tall (`kb` > 0) and pans the visual one; Android with
 * `interactiveWidget: resizes-content` shrinks the layout viewport (`kb` stays 0), so the keyboard is
 * also recognised by the visible height falling below the tallest one seen (`baseline`).
 */
export function readViewportBox(vv: ViewportSample, innerHeight: number, baseline: number): ViewportBox {
  const kb = Math.max(0, Math.round(innerHeight - vv.height - vv.offsetTop));
  return {
    width: vv.width,
    height: vv.height,
    top: Math.max(0, vv.offsetTop),
    left: Math.max(0, vv.offsetLeft),
    kb,
    keyboard: kb > KEYBOARD_MIN || baseline - vv.height > KEYBOARD_MIN,
  };
}

/** The custom properties a layer carries so CSS can size itself from the box (`styles/sheet.css` reads them with fallbacks). */
export function boxVars(box: ViewportBox): Record<string, string> {
  return {
    "--vvh": `${box.height}px`,
    "--vvw": `${box.width}px`,
    "--vv-top": `${box.top}px`,
    "--vv-left": `${box.left}px`,
    "--kb": `${box.kb}px`,
  };
}

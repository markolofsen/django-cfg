/**
 * One hook for the installed app's viewport: `--app-height` and a shell that sits at scroll 0.
 *
 * Why it exists (all three are iOS standalone behaviours, see `@docs/PWA_AND_MOBILE.md`):
 *  1. At launch `innerHeight`/`dvh` can be short by the top inset while `lvh` is right, so the shell height
 *     (`--app-height`) is the largest of `lvh`, `dvh`, `innerHeight`, capped at the screen.
 *  2. The viewport can shrink for real with no keyboard (seen after an in-app browser sheet is closed: `innerHeight`
 *     812 -> 771, `lvh` stayed 812). A larger `innerHeight` WAS seen earlier this session and it dropped, so `lvh` is not
 *     trusted any more and the height follows `max(innerHeight, dvh)` until `innerHeight` grows back.
 *  3. A locked shell (`data-private-shell`, `overflow: hidden`) is still scrolled by the browser (a field lifted over the
 *     keyboard, a restored scroll position) and the reader cannot drag it back: window, html, body and the
 *     `[data-app-shell]` element are put back at 0.
 *
 * It does nothing outside an installed app, while the keyboard is up (it resizes the visual viewport, not the app) or on a
 * pinch-zoomed page. Every trigger runs the same `settle`: now, and again after 300 ms, because iOS reports the final size
 * late. A page-wide scroll is put back on the next frame.
 */

import { detectDisplayMode, isInstalledMode, subscribeDisplayMode } from './displayMode';

const PROP = '--app-height';
const SHELL = '[data-app-shell]';
/** A drop of this many px below the largest `innerHeight` seen is a real shrink, not rounding or a bar animating. */
const SHRINK_PX = 8;
const SETTLE_MS = 300;
const LOG_SIZE = 5;

export interface ViewportChange {
  at: number;
  trigger: string;
  /** What was changed, e.g. `--app-height 812 -> 771`, `shell 0,59`. */
  what: string[];
}

const log: ViewportChange[] = [];

/** The last changes made (heights and scroll resets), oldest first, for the Debug HUD. */
export function getViewportLog(): readonly ViewportChange[] {
  return log;
}

export function locked(): boolean {
  return document.documentElement.hasAttribute('data-private-shell') && isInstalledMode(detectDisplayMode());
}

/** True while the keyboard (or any other inset) covers part of the layout viewport. */
export function keyboardUp(): boolean {
  const vv = window.visualViewport;
  return Boolean(vv) && window.innerHeight - vv!.height > 80;
}

function zoomed(): boolean {
  return Boolean(window.visualViewport) && window.visualViewport!.scale > 1.01;
}

export function probeHeight(unit: 'lvh' | 'dvh' | 'svh'): number {
  if (typeof CSS !== 'undefined' && CSS.supports && !CSS.supports('height', `100${unit}`)) return 0;
  const el = document.createElement('div');
  el.style.cssText = `position:fixed;top:0;left:0;width:0;height:100${unit};visibility:hidden;pointer-events:none`;
  document.body.appendChild(el);
  const h = el.getBoundingClientRect().height;
  el.remove();
  return h;
}

function capped(h: number): number {
  const screenMax = Math.max(window.screen?.height || 0, window.screen?.width || 0);
  return screenMax > 0 ? Math.min(h, screenMax) : h;
}

/** Puts window, html, body and the shell back at 0; returns what had to move. */
function zeroScroll(): string[] {
  const what: string[] = [];
  if (window.scrollX || window.scrollY) what.push(`window ${Math.round(window.scrollX)},${Math.round(window.scrollY)}`);
  window.scrollTo(0, 0);
  for (const [name, el] of [['html', document.documentElement], ['body', document.body]] as const) {
    if (el.scrollTop) {
      what.push(`${name} ${Math.round(el.scrollTop)}`);
      el.scrollTop = 0;
    }
  }
  for (const el of document.querySelectorAll<HTMLElement>(SHELL)) {
    if (el.scrollTop || el.scrollLeft) {
      what.push(`shell ${Math.round(el.scrollLeft)},${Math.round(el.scrollTop)}`);
      el.scrollTop = 0;
      el.scrollLeft = 0;
    }
  }
  return what;
}

let remeasure: (() => string[]) | null = null;

/** The Debug section's "Re-measure now": runs the whole thing at once and returns what it changed. */
export function remeasureViewport(): string[] {
  return remeasure?.() ?? [];
}

/** Installs every trigger. Returns a cleanup. */
export function syncViewport(): () => void {
  if (typeof window === 'undefined' || typeof document === 'undefined') return () => {};
  const root = document.documentElement;
  let peakInner = 0;
  let frame = 0;
  const timers: number[] = [];

  const run = (trigger: string): string[] => {
    if (!isInstalledMode(detectDisplayMode())) {
      root.style.removeProperty(PROP);
      return [];
    }
    if (keyboardUp() || zoomed()) return [];
    const what: string[] = [];
    const inner = window.innerHeight;
    peakInner = Math.max(peakInner, inner);
    const h = peakInner - inner >= SHRINK_PX ? Math.max(inner, probeHeight('dvh')) : Math.max(probeHeight('lvh'), probeHeight('dvh'), inner);
    const next = Math.round(capped(h));
    const prev = parseFloat(root.style.getPropertyValue(PROP)) || null;
    if (next > 0 && prev !== next) {
      root.style.setProperty(PROP, `${next}px`);
      what.push(`${PROP} ${prev ?? '-'} -> ${next}`);
    }
    if (locked()) what.push(...zeroScroll());
    if (what.length) {
      log.push({ at: Date.now(), trigger, what });
      if (log.length > LOG_SIZE) log.shift();
    }
    return what;
  };

  const settle = (trigger: string) => {
    run(trigger);
    timers.push(window.setTimeout(() => run(trigger), SETTLE_MS));
  };
  remeasure = () => {
    peakInner = 0; // a manual look trusts the viewport as it is now
    return run('manual');
  };

  const onResize = () => settle('resize');
  const onVisualViewport = () => settle('viewport-resize');
  const onPageShow = () => settle('pageshow');
  const onFocus = () => settle('focus');
  const onFocusOut = () => settle('focusout');
  const onOrientation = () => {
    peakInner = 0; // landscape is not a shrink of portrait
    settle('orientation');
  };
  const onVisible = () => {
    if (document.visibilityState === 'visible') settle('visible');
  };
  // `scroll` does not bubble: the capture phase is how a scroll of the shell element is seen.
  const onScroll = (event: Event) => {
    const t = event.target;
    if (frame || !(t === document || (t instanceof Element && t.matches(SHELL)))) return;
    frame = window.requestAnimationFrame(() => {
      frame = 0;
      if (locked() && !keyboardUp() && !zoomed()) {
        const what = zeroScroll();
        if (what.length) {
          log.push({ at: Date.now(), trigger: 'scroll', what });
          if (log.length > LOG_SIZE) log.shift();
        }
      }
    });
  };

  const vv = window.visualViewport;
  const stopDisplay = subscribeDisplayMode(() => settle('display-mode'));
  run('init');
  window.addEventListener('resize', onResize);
  vv?.addEventListener('resize', onVisualViewport);
  window.addEventListener('pageshow', onPageShow);
  window.addEventListener('focus', onFocus);
  window.addEventListener('orientationchange', onOrientation);
  document.addEventListener('focusout', onFocusOut);
  document.addEventListener('visibilitychange', onVisible);
  document.addEventListener('scroll', onScroll, { capture: true, passive: true });
  return () => {
    window.removeEventListener('resize', onResize);
    vv?.removeEventListener('resize', onVisualViewport);
    window.removeEventListener('pageshow', onPageShow);
    window.removeEventListener('focus', onFocus);
    window.removeEventListener('orientationchange', onOrientation);
    document.removeEventListener('focusout', onFocusOut);
    document.removeEventListener('visibilitychange', onVisible);
    document.removeEventListener('scroll', onScroll, { capture: true });
    stopDisplay();
    if (frame) window.cancelAnimationFrame(frame);
    timers.forEach((t) => window.clearTimeout(t));
    remeasure = null;
    root.style.removeProperty(PROP);
  };
}

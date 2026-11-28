/**
 * Viewport HUD for chasing a displaced installed app. The state is one of `off`, `dot`, `small`, `medium`, `full`:
 *   - the Debug section of the Settings dialog (`@djangocfg/layouts`, `builtins.debug`) switches `off` <-> `small`;
 *   - tapping the HUD cycles small -> medium -> full -> dot; tapping the dot (24px, semi-transparent, in a corner) goes
 *     back to small. Only the HUD box and the dot take pointer events; the rest of the screen is untouched.
 *   - a host with no Settings dialog (a call page) passes `debug` to `UiProviders`: with nothing stored the state is `dot`.
 * The state lives in `localStorage`, which is per origin (a failed read or write degrades to the default / this page view).
 * `syncViewportDebug` (mounted by `UiProviders`) draws it over the app, so the bug can be photographed outside the dialog.
 */

import { detectDisplayMode } from './displayMode';
import { getViewportLog, keyboardUp, locked, probeHeight } from './viewportSync';

const KEY = 'viewportdebug';

export type HudState = 'off' | 'dot' | 'small' | 'medium' | 'full';
const STATES: readonly HudState[] = ['off', 'dot', 'small', 'medium', 'full'];

let memory: HudState | null = null;
const listeners = new Set<() => void>();

/** The stored state, else `fallback` (`dot` for a host that passed `debug`, otherwise `off`). */
export function getViewportHud(fallback: HudState = 'off'): HudState {
  try {
    const v = window.localStorage.getItem(KEY) as HudState | null;
    return v && STATES.includes(v) ? v : fallback;
  } catch {
    return memory ?? fallback; // storage blocked: this page view only
  }
}

export function setViewportHud(state: HudState): void {
  memory = state;
  try {
    window.localStorage.setItem(KEY, state);
  } catch {
    /* private mode: kept for this page view */
  }
  listeners.forEach((l) => l());
}

export function subscribeViewportHud(onChange: () => void): () => void {
  listeners.add(onChange);
  window.addEventListener('storage', onChange);
  return () => {
    listeners.delete(onChange);
    window.removeEventListener('storage', onChange);
  };
}

/** One tap on the HUD: small -> medium -> full -> dot; one tap on the dot: small. */
export function nextViewportHud(state: HudState): HudState {
  return ({ off: 'off', dot: 'small', small: 'medium', medium: 'full', full: 'dot' } as const)[state];
}

/** `env(safe-area-inset-*)` as the browser resolves it right now, read off a probe element. */
function safeInsets(): string {
  const el = document.createElement('div');
  el.style.cssText =
    'position:fixed;top:0;left:0;visibility:hidden;pointer-events:none;padding:env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)';
  document.body.appendChild(el);
  const cs = getComputedStyle(el);
  const out = [cs.paddingTop, cs.paddingRight, cs.paddingBottom, cs.paddingLeft].map((v) => parseFloat(v) || 0).join('/');
  el.remove();
  return out;
}

const n = (v: number | undefined) => (v === undefined ? '-' : String(Math.round(v * 100) / 100));

function rectOf(el: Element | null): string {
  if (!el) return 'none';
  const r = el.getBoundingClientRect();
  return `top ${n(r.top)} h ${n(r.height)}`;
}

function scrollOf(el: Element | null): string {
  return el ? `top ${n(el.scrollTop)} sh ${n(el.scrollHeight)} ch ${n(el.clientHeight)}` : 'none';
}

export type HudLevel = 'small' | 'medium' | 'full';

/** The text the HUD prints at a level; pure over the live DOM so a test can read it. `full` is everything. */
export function viewportSnapshot(now: number = Date.now(), level: HudLevel = 'full'): string {
  const vv = window.visualViewport;
  const root = document.documentElement;
  const shell = document.querySelector<HTMLElement>('[data-app-shell]');
  const bar = document.querySelector('[data-sidebar="topbar"]');
  const appHeight = getComputedStyle(root).getPropertyValue('--app-height').trim() || '(unset)';
  const ago = (at: number) => `${((now - at) / 1000).toFixed(1)}s ago`;
  const changes = getViewportLog().map((c) => `${ago(c.at)} ${c.trigger}: ${c.what.join(', ')}`);
  const mode = `mode ${detectDisplayMode()}  locked ${locked()}  kbd ${keyboardUp()}`;

  if (level === 'small') {
    return `${detectDisplayMode()} ih ${n(window.innerHeight)} app ${appHeight} sy ${n(window.scrollY)} shell ${shell ? n(shell.getBoundingClientRect().top) : '-'}`;
  }
  const core = [
    mode,
    `scrollY ${n(window.scrollY)}  shell.scrollTop ${shell ? n(shell.scrollTop) : 'no shell'}`,
    `innerHeight ${n(window.innerHeight)}  --app-height ${appHeight}`,
    `vv h ${n(vv?.height)}  top ${n(vv?.offsetTop)}  scale ${n(vv?.scale)}`,
    `shell ${rectOf(shell)}`,
    `top bar ${rectOf(bar)}`,
  ];
  if (level === 'medium') {
    return [...core, `last change: ${changes.at(-1) ?? '(none)'}`].join('\n');
  }
  return [
    ...core,
    `lvh ${n(probeHeight('lvh'))}  dvh ${n(probeHeight('dvh'))}  svh ${n(probeHeight('svh'))}`,
    `screen.height ${n(window.screen?.height)}  outerHeight ${n(window.outerHeight)}`,
    `safe t/r/b/l ${safeInsets()}`,
    `scrollingElement ${scrollOf(document.scrollingElement)}`,
    `html ${scrollOf(root)}  ${rectOf(root)}`,
    `body ${scrollOf(document.body)}  ${rectOf(document.body)}`,
    `body style: ${document.body.style.cssText || '(none)'}`,
    `body attr: ${document.body.hasAttribute('data-scroll-locked') ? 'data-scroll-locked' : '(none)'}`,
    `html style: ${root.style.cssText || '(none)'}`,
    `changes (last ${changes.length}):`,
    ...(changes.length ? changes.map((c) => `  ${c}`) : ['  (none)']),
  ].join('\n');
}

const BOX =
  'position:fixed;z-index:2147483647;margin:0;font:10px/1.35 ui-monospace,Menlo,monospace;white-space:pre-wrap;word-break:break-all;';

function mountHud(state: 'small' | 'medium' | 'full'): () => void {
  const hud = document.createElement('pre');
  hud.setAttribute('data-viewport-debug', state);
  hud.style.cssText = `${BOX}left:0;right:0;bottom:0;padding:6px 8px;color:#0f0;background:rgba(0,0,0,.82);cursor:pointer`;
  hud.addEventListener('click', () => setViewportHud(nextViewportHud(state)));
  const draw = () => {
    hud.textContent = viewportSnapshot(Date.now(), state);
  };
  document.body.appendChild(hud);
  draw();
  const id = window.setInterval(draw, 400);
  window.addEventListener('scroll', draw, true);
  window.addEventListener('resize', draw);
  window.visualViewport?.addEventListener('resize', draw);
  window.visualViewport?.addEventListener('scroll', draw);
  return () => {
    window.clearInterval(id);
    window.removeEventListener('scroll', draw, true);
    window.removeEventListener('resize', draw);
    window.visualViewport?.removeEventListener('resize', draw);
    window.visualViewport?.removeEventListener('scroll', draw);
    hud.remove();
  };
}

function mountDot(): () => void {
  const dot = document.createElement('div');
  dot.setAttribute('data-viewport-debug', 'dot');
  dot.style.cssText = `${BOX}left:8px;bottom:calc(env(safe-area-inset-bottom,0px) + 8px);width:24px;height:24px;border-radius:50%;background:rgba(0,255,0,.35);cursor:pointer`;
  dot.addEventListener('click', () => setViewportHud(nextViewportHud('dot')));
  document.body.appendChild(dot);
  return () => dot.remove();
}

/** Draws whatever the stored state says, and follows it. `debug` makes `dot` the default instead of `off`. Returns a cleanup. */
export function syncViewportDebug({ debug = false }: { debug?: boolean } = {}): () => void {
  if (typeof window === 'undefined' || typeof document === 'undefined') return () => {};
  let shown: HudState = 'off';
  let unmount: (() => void) | null = null;
  const apply = () => {
    const state = getViewportHud(debug ? 'dot' : 'off');
    if (state === shown) return;
    unmount?.();
    unmount = state === 'off' ? null : state === 'dot' ? mountDot() : mountHud(state);
    shown = state;
  };
  apply();
  const stop = subscribeViewportHud(apply);
  return () => {
    stop();
    unmount?.();
  };
}

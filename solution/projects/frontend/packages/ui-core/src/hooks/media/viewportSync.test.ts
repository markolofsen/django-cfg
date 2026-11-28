// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { getViewportLog, remeasureViewport, syncViewport } from './viewportSync';

const root = document.documentElement;
const prop = () => root.style.getPropertyValue('--app-height');

let inner = 812;
let vv = { height: 812, scale: 1 };

function setInner(h: number) {
  inner = h;
  window.dispatchEvent(new Event('resize'));
}

beforeEach(() => {
  vi.useFakeTimers();
  inner = 812;
  vv = { height: 812, scale: 1 };
  Object.defineProperty(window, 'innerHeight', { configurable: true, get: () => inner });
  Object.defineProperty(window, 'visualViewport', { configurable: true, value: Object.defineProperties(new EventTarget(), { height: { get: () => vv.height }, scale: { get: () => vv.scale } }) });
  Object.defineProperty(window.navigator, 'standalone', { configurable: true, value: true });
  window.scrollTo = vi.fn() as unknown as typeof window.scrollTo;
  root.setAttribute('data-private-shell', '');
});

afterEach(() => {
  vi.useRealTimers();
  root.removeAttribute('data-private-shell');
  root.style.removeProperty('--app-height');
  document.body.innerHTML = '';
  Object.defineProperty(window.navigator, 'standalone', { configurable: true, value: undefined });
});

describe('syncViewport: --app-height', () => {
  it('sets the height at init and removes it on cleanup', () => {
    const stop = syncViewport();
    expect(prop()).toBe('812px');
    stop();
    expect(prop()).toBe('');
  });

  it('follows a real shrink with no keyboard once it has held 300 ms (812 -> 771)', () => {
    const stop = syncViewport();
    setInner(771);
    window.dispatchEvent(new Event('pageshow'));
    vi.advanceTimersByTime(300);
    expect(prop()).toBe('771px');
    expect(getViewportLog().at(-1)?.what[0]).toContain('812 -> 771');
    stop();
  });

  it('applies the largest rule again when the height grows back', () => {
    const stop = syncViewport();
    setInner(771);
    vi.advanceTimersByTime(300);
    setInner(812);
    vi.advanceTimersByTime(300);
    expect(prop()).toBe('812px');
    stop();
  });

  it('ignores a keyboard-sized change and a pinch-zoom', () => {
    const stop = syncViewport();
    inner = 812;
    vv = { height: 500, scale: 1 }; // keyboard: only the visual viewport shrinks
    window.dispatchEvent(new Event('resize'));
    vi.advanceTimersByTime(300);
    expect(prop()).toBe('812px');
    vv = { height: 812, scale: 2 };
    setInner(600);
    vi.advanceTimersByTime(300);
    expect(prop()).toBe('812px');
    stop();
  });

  it('does nothing in a browser tab', () => {
    Object.defineProperty(window.navigator, 'standalone', { configurable: true, value: false });
    const stop = syncViewport();
    expect(prop()).toBe('');
    stop();
  });

  it('a manual re-measure trusts the viewport as it is', () => {
    const stop = syncViewport();
    inner = 771; // no event: only the button looks
    expect(remeasureViewport().join()).toContain('-> 771');
    expect(prop()).toBe('771px');
    stop();
  });
});

describe('syncViewport: scroll back to 0', () => {
  function shell() {
    const el = document.createElement('div');
    el.setAttribute('data-app-shell', '');
    document.body.appendChild(el);
    return el;
  }

  it('puts a scrolled shell back on the next frame', async () => {
    const el = shell();
    const stop = syncViewport();
    el.scrollTop = 59;
    el.dispatchEvent(new Event('scroll'));
    vi.advanceTimersByTime(50);
    expect(el.scrollTop).toBe(0);
    expect(getViewportLog().at(-1)?.trigger).toBe('scroll');
    stop();
  });

  it('leaves it alone while the keyboard is up', () => {
    const el = shell();
    const stop = syncViewport();
    vv = { height: 450, scale: 1 };
    el.scrollTop = 59;
    el.dispatchEvent(new Event('scroll'));
    vi.advanceTimersByTime(50);
    expect(el.scrollTop).toBe(59);
    stop();
  });

  it('manual re-measure zeroes scrollers and reports them', () => {
    const el = shell();
    const stop = syncViewport();
    el.scrollTop = 41;
    expect(remeasureViewport().some((w) => w.startsWith('shell'))).toBe(true);
    expect(el.scrollTop).toBe(0);
    stop();
  });
});

// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { getViewportHud, nextViewportHud, setViewportHud, syncViewportDebug, viewportSnapshot } from './viewportDebug';

const hud = () => document.querySelector<HTMLElement>('[data-viewport-debug]');

beforeEach(() => localStorage.clear());
afterEach(() => {
  document.body.innerHTML = '';
  localStorage.clear();
});

describe('viewport HUD', () => {
  it('is off by default and persists a state', () => {
    expect(getViewportHud()).toBe('off');
    setViewportHud('medium');
    expect(localStorage.getItem('viewportdebug')).toBe('medium');
    expect(getViewportHud()).toBe('medium');
  });

  it('cycles small, medium, full, dot, small', () => {
    expect(['small', 'medium', 'full', 'dot'].map((s) => nextViewportHud(s as never))).toEqual(['medium', 'full', 'dot', 'small']);
  });

  it('a tap on the HUD advances it; the dot is 24px and a tap brings small back', () => {
    setViewportHud('small');
    const stop = syncViewportDebug();
    expect(hud()?.getAttribute('data-viewport-debug')).toBe('small');
    hud()!.click();
    expect(hud()?.getAttribute('data-viewport-debug')).toBe('medium');
    hud()!.click();
    hud()!.click();
    expect(hud()?.getAttribute('data-viewport-debug')).toBe('dot');
    expect(hud()!.style.width).toBe('24px');
    hud()!.click();
    expect(hud()?.getAttribute('data-viewport-debug')).toBe('small');
    stop();
    expect(hud()).toBeNull();
  });

  it('`debug` shows the dot when nothing is stored; a stored state wins', () => {
    let stop = syncViewportDebug({ debug: true });
    expect(hud()?.getAttribute('data-viewport-debug')).toBe('dot');
    stop();
    setViewportHud('off');
    stop = syncViewportDebug({ debug: true });
    expect(hud()).toBeNull();
    stop();
  });

  it('small is shorter than full', () => {
    expect(viewportSnapshot(Date.now(), 'small').length).toBeLessThan(viewportSnapshot(Date.now(), 'full').length);
  });

  it('survives broken storage', () => {
    const orig = Storage.prototype.getItem;
    Storage.prototype.getItem = () => { throw new Error('blocked'); };
    expect(() => getViewportHud('dot')).not.toThrow();
    Storage.prototype.getItem = orig;
  });
});

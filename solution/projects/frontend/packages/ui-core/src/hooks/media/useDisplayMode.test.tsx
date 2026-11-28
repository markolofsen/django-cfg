import * as React from 'react';
import { renderToString } from 'react-dom/server';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { detectDisplayMode, subscribeDisplayMode, syncDisplayModeAttribute } from './displayMode';
import { useIsPwa } from './useDisplayMode';

// Node environment: window/document are stubbed per test.
function stubBrowser(active: string[], extra: { standalone?: boolean; referrer?: string } = {}) {
  const listeners = new Set<() => void>();
  const attrs: Record<string, string> = {};
  vi.stubGlobal('window', {
    matchMedia: (q: string) => ({
      matches: active.some((m) => q === `(display-mode: ${m})`),
      addEventListener: (_: string, l: () => void) => listeners.add(l),
      removeEventListener: (_: string, l: () => void) => listeners.delete(l),
    }),
    navigator: { standalone: extra.standalone },
  });
  vi.stubGlobal('document', {
    referrer: extra.referrer ?? '',
    documentElement: { setAttribute: (k: string, v: string) => (attrs[k] = v) },
  });
  return { attrs, fire: () => listeners.forEach((l) => l()), size: () => listeners.size, set: (m: string[]) => active.splice(0, active.length, ...m) };
}

afterEach(() => vi.unstubAllGlobals());

describe('display mode', () => {
  it('server render reports browser (no hydration mismatch)', () => {
    function Probe() {
      return <span>{String(useIsPwa())}</span>;
    }
    expect(renderToString(<Probe />)).toContain('false');
    expect(detectDisplayMode()).toBe('browser');
  });

  it('reads the display-mode media query', () => {
    stubBrowser(['standalone']);
    expect(detectDisplayMode()).toBe('standalone');
  });

  it('detects iOS navigator.standalone when the media query does not match', () => {
    stubBrowser([], { standalone: true });
    expect(detectDisplayMode()).toBe('standalone');
  });

  it('detects the Android TWA referrer', () => {
    stubBrowser([], { referrer: 'android-app://com.example' });
    expect(detectDisplayMode()).toBe('standalone');
  });

  it('notifies subscribers on media query change and unsubscribes cleanly', () => {
    const b = stubBrowser([]);
    const onChange = vi.fn();
    const stop = subscribeDisplayMode(onChange);
    b.fire();
    expect(onChange).toHaveBeenCalledTimes(1);
    stop();
    expect(b.size()).toBe(0);
  });

  it('keeps <html data-display-mode> in sync', () => {
    const b = stubBrowser([]);
    const stop = syncDisplayModeAttribute();
    expect(b.attrs['data-display-mode']).toBe('browser');
    b.set(['fullscreen']);
    b.fire();
    expect(b.attrs['data-display-mode']).toBe('fullscreen');
    stop();
  });
});

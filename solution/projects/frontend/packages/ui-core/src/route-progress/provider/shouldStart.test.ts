import { describe, expect, it } from 'vitest';

import { createNavigationBehaviorStore } from '../behavior/store';
import { createProgressEngine } from '../engine/createProgressEngine';
import type { RouteProgressContextValue } from './context';
import { shouldStartProgress } from './shouldStart';

const url = (p: string) => new URL(p, 'http://site.test');
const ctx = (over: Partial<RouteProgressContextValue> = {}): RouteProgressContextValue => ({
  engine: createProgressEngine(),
  behavior: createNavigationBehaviorStore(),
  enabled: true,
  ...over,
});

describe('shouldStartProgress', () => {
  it('no provider: never', () => {
    expect(shouldStartProgress(null, url('/a'), url('/b'), true)).toBe(false);
  });

  it('default: pathname change only', () => {
    const c = ctx();
    expect(shouldStartProgress(c, url('/a'), url('/b'))).toBe(true);
    expect(shouldStartProgress(c, url('/a?x=1'), url('/a?x=2'))).toBe(false);
    expect(shouldStartProgress(c, url('/a'), url('/a#top'))).toBe(false);
  });

  it('the explicit option beats a page lease', () => {
    const c = ctx();
    c.behavior.acquire({ progress: false });
    expect(shouldStartProgress(c, url('/a'), url('/b'))).toBe(false);
    expect(shouldStartProgress(c, url('/a'), url('/b'), true)).toBe(true);
    expect(shouldStartProgress(c, url('/a'), url('/a?x=1'), true)).toBe(true);
  });

  it('the app switch beats even an explicit true', () => {
    expect(shouldStartProgress(ctx({ enabled: false }), url('/a'), url('/b'), true)).toBe(false);
  });

  it('shouldShow replaces the default rule but not a page lease', () => {
    const c = ctx({ shouldShow: (_f, to) => !to.pathname.startsWith('/board') });
    expect(shouldStartProgress(c, url('/a'), url('/board/1'))).toBe(false);
    expect(shouldStartProgress(c, url('/a'), url('/a?x=1'))).toBe(true);
    c.behavior.acquire({ progress: false });
    expect(shouldStartProgress(c, url('/a'), url('/b'))).toBe(false);
  });
});

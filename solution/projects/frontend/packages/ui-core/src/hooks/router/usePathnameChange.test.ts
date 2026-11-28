// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { watchPathname } from './usePathnameChange';

/** `pushState` dispatches its event in a microtask (see `patchHistoryOnce`). */
const settle = () => Promise.resolve().then(() => undefined);

let stop: (() => void) | undefined;

beforeEach(() => {
  window.history.replaceState(null, '', '/start?x=1');
});

afterEach(() => {
  stop?.();
  stop = undefined;
});

describe('watchPathname', () => {
  it('fires on a push to another path with the new and the previous path', async () => {
    const seen = vi.fn();
    stop = watchPathname(seen);
    window.history.pushState(null, '', '/auth');
    await settle();
    expect(seen).toHaveBeenCalledTimes(1);
    expect(seen).toHaveBeenCalledWith('/auth', '/start');
  });

  it('fires on replace and on back/forward (popstate)', async () => {
    const seen = vi.fn();
    stop = watchPathname(seen);
    window.history.replaceState(null, '', '/other');
    await settle();
    expect(seen).toHaveBeenLastCalledWith('/other', '/start');
    window.history.replaceState(null, '', '/popped');
    window.dispatchEvent(new PopStateEvent('popstate'));
    expect(seen).toHaveBeenLastCalledWith('/popped', '/other');
  });

  it('ignores a change of the query or the hash only', async () => {
    const seen = vi.fn();
    stop = watchPathname(seen);
    window.history.pushState(null, '', '/start?x=2');
    window.history.replaceState(null, '', '/start?x=3#top');
    await settle();
    expect(seen).not.toHaveBeenCalled();
  });

  it('does not fire for the path it started on, and tracks the latest path afterwards', async () => {
    const seen = vi.fn();
    stop = watchPathname(seen);
    await settle();
    expect(seen).not.toHaveBeenCalled();
    window.history.pushState(null, '', '/a');
    await settle();
    window.history.pushState(null, '', '/a?q=1');
    window.history.pushState(null, '', '/b');
    await settle();
    expect(seen.mock.calls).toEqual([
      ['/a', '/start'],
      ['/b', '/a'],
    ]);
  });

  it('stops listening after the unsubscribe', async () => {
    const seen = vi.fn();
    watchPathname(seen)();
    window.history.pushState(null, '', '/gone');
    await settle();
    expect(seen).not.toHaveBeenCalled();
  });
});

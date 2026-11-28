// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import {
  CHUNK_RELOAD_STORAGE_KEY,
  CHUNK_RELOAD_WINDOW_MS,
  canAutoReloadForChunk,
  installChunkReloadListeners,
  isChunkLoadError,
  isStaticAssetLoadEvent,
  reloadForChunkError,
} from '@djangocfg/ui-core/lib';

describe('isChunkLoadError', () => {
  it.each([
    ['ChunkLoadError by name', Object.assign(new Error('x'), { name: 'ChunkLoadError' })],
    ['webpack JS chunk', new Error('Loading chunk 123 failed.\n(error: /_next/static/chunks/123.js)')],
    ['webpack CSS chunk', new Error('Loading CSS chunk 45 failed.')],
    ['Chrome dynamic import', new TypeError('Failed to fetch dynamically imported module: /_next/static/a.js')],
    ['Firefox dynamic import', new TypeError('error loading dynamically imported module')],
    ['Safari module script', new TypeError('Importing a module script failed.')],
    ['cancelled fetch of static asset', new TypeError('Failed to fetch /_next/static/chunks/app/page-abc.js')],
    ['aborted static asset via stack', Object.assign(new Error('signal is aborted'), { stack: 'at https://x.io/_next/static/chunks/1.js:1' })],
    ['string reason', 'Loading chunk 9 failed.'],
  ])('detects %s', (_n, err) => expect(isChunkLoadError(err)).toBe(true));

  it.each([
    ['ordinary error', new Error('Cannot read properties of undefined')],
    ['API fetch failure', new TypeError('Failed to fetch https://api.example.com/items')],
    ['null', null],
    ['undefined', undefined],
  ])('ignores %s', (_n, err) => expect(isChunkLoadError(err)).toBe(false));
});

describe('isStaticAssetLoadEvent', () => {
  it('matches failed script/link under /_next/static and nothing else', () => {
    const script = document.createElement('script');
    script.src = 'https://x.io/_next/static/chunks/1.js';
    const other = document.createElement('script');
    other.src = 'https://cdn.io/lib.js';
    const link = document.createElement('link');
    link.href = 'https://x.io/_next/static/css/a.css';
    const mk = (target: Element) => Object.defineProperty(new Event('error'), 'target', { value: target });
    expect(isStaticAssetLoadEvent(mk(script))).toBe(true);
    expect(isStaticAssetLoadEvent(mk(link))).toBe(true);
    expect(isStaticAssetLoadEvent(mk(other))).toBe(false);
  });
});

describe('reload guard', () => {
  const reload = vi.fn();
  beforeEach(() => {
    sessionStorage.clear();
    reload.mockClear();
    Object.defineProperty(window, 'location', { configurable: true, value: { ...window.location, reload } });
  });
  afterEach(() => vi.restoreAllMocks());

  it('reloads once, then blocks a second reload inside the window', () => {
    expect(reloadForChunkError(1_000)).toBe(true);
    expect(sessionStorage.getItem(CHUNK_RELOAD_STORAGE_KEY)).toBe('1000');
    expect(reloadForChunkError(1_000 + 5_000)).toBe(false);
    expect(reload).toHaveBeenCalledTimes(1);
  });

  it('allows another reload after the window passes', () => {
    reloadForChunkError(1_000);
    expect(canAutoReloadForChunk(1_000 + CHUNK_RELOAD_WINDOW_MS + 1)).toBe(true);
  });

  it('never reloads when sessionStorage is unusable (no loop risk)', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('denied');
    });
    expect(canAutoReloadForChunk()).toBe(false);
    expect(reloadForChunkError()).toBe(false);
    expect(reload).not.toHaveBeenCalled();
  });

  it('window listeners reload once for an unhandled chunk rejection', () => {
    const off = installChunkReloadListeners();
    const ev = new Event('unhandledrejection') as Event & { reason?: unknown };
    ev.reason = new Error('Loading chunk 7 failed.');
    window.dispatchEvent(ev);
    window.dispatchEvent(ev);
    expect(reload).toHaveBeenCalledTimes(1);
    off();
  });
});

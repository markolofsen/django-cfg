import { afterEach, describe, expect, it } from 'vitest';

import {
  clearStorageNamespace,
  createStorageNamespace,
  evictableKeys,
  isEvictableKey,
  isSchemeKey,
  listStorageKeys,
  resolveStorageKey,
} from './storage-namespace';

class MemoryStorage implements Storage {
  private map = new Map<string, string>();
  get length() {
    return this.map.size;
  }
  clear() {
    this.map.clear();
  }
  getItem(key: string) {
    return this.map.get(key) ?? null;
  }
  key(index: number) {
    return [...this.map.keys()][index] ?? null;
  }
  removeItem(key: string) {
    this.map.delete(key);
  }
  setItem(key: string, value: string) {
    this.map.set(key, value);
  }
}

const g = globalThis as unknown as { window?: unknown };

function fakeWindow() {
  const local = new MemoryStorage();
  const session = new MemoryStorage();
  g.window = { localStorage: local, sessionStorage: session };
  return { local, session };
}

afterEach(() => {
  delete g.window;
});

describe('resolveStorageKey', () => {
  it('keeps keys that already follow the scheme', () => {
    expect(resolveStorageKey('kino.player.volume', 'cfg')).toBe('kino.player.volume');
    expect(resolveStorageKey('cfg.ui.state')).toBe('cfg.ui.state');
  });

  it('places a bare name under <owner>.ui.<snake_case>', () => {
    expect(resolveStorageKey('search-filter')).toBe('cfg.ui.search_filter');
    expect(resolveStorageKey('Last Volume', 'kino')).toBe('kino.ui.last_volume');
  });

  it('throws when nothing usable is left', () => {
    expect(() => resolveStorageKey('---')).toThrow(TypeError);
  });

  it('recognises scheme keys', () => {
    expect(isSchemeKey('cfg.chat.draft.room_1')).toBe(true);
    expect(isSchemeKey('NEXT_LOCALE')).toBe(false);
    expect(isSchemeKey('sidebar-width')).toBe(false);
  });
});

describe('eviction', () => {
  it('never evicts personal, auth or third-party keys', () => {
    expect(isEvictableKey('cfg.auth.access_token')).toBe(false);
    expect(isEvictableKey('cfg.profile.cache')).toBe(false);
    expect(isEvictableKey('cfg.chat.draft.room_1')).toBe(false);
    expect(isEvictableKey('NEXT_LOCALE')).toBe(false);
    expect(isEvictableKey('cfg.ui.state')).toBe(true);
    expect(isEvictableKey('kino.player.volume')).toBe(true);
  });

  it('lists only evictable names of a store', () => {
    const { local } = fakeWindow();
    local.setItem('cfg.auth.access_token', 't');
    local.setItem('NEXT_LOCALE', 'en');
    local.setItem('cfg.ui.tab', '1');
    expect(evictableKeys(local)).toEqual(['cfg.ui.tab']);
  });
});

describe('namespace inspection and reset', () => {
  it('lists the keys of one owner', () => {
    const { local } = fakeWindow();
    local.setItem('kino.player.volume', '1');
    local.setItem('cfg.ui.tab', '1');
    expect(listStorageKeys('kino')).toEqual(['kino.player.volume']);
  });

  it('keeps personal cfg keys unless asked', () => {
    const { local, session } = fakeWindow();
    local.setItem('cfg.auth.access_token', 't');
    local.setItem('cfg.ui.tab', '1');
    session.setItem('cfg.ui.wizard', '2');
    expect(clearStorageNamespace('cfg').sort()).toEqual(['cfg.ui.tab', 'cfg.ui.wizard']);
    expect(local.getItem('cfg.auth.access_token')).toBe('t');
    clearStorageNamespace('cfg', { includePersonal: true });
    expect(local.getItem('cfg.auth.access_token')).toBeNull();
  });

  it('createStorageNamespace builds owner keys and clears them', () => {
    const { local } = fakeWindow();
    const kino = createStorageNamespace('kino');
    expect(kino.key('player', 'Last Volume')).toBe('kino.player.last_volume');
    local.setItem('kino.player.volume', '1');
    expect(kino.keys()).toEqual(['kino.player.volume']);
    kino.clear();
    expect(kino.keys()).toEqual([]);
  });
});

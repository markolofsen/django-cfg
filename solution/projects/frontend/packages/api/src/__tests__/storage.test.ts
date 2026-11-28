// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { CFG_FAMILIES, CFG_KEYS, cfgStorage, createStorage, normalizeSegment } from '../storage';

const SCHEME = /^cfg(\.[a-z0-9_]+)+$/;

beforeEach(() => {
  localStorage.clear();
  sessionStorage.clear();
  document.cookie.split('; ').forEach((c) => {
    document.cookie = `${c.split('=')[0]}=; Max-Age=0; Path=/`;
  });
  cfgStorage.clearAll({ all: true });
});

describe('registry', () => {
  it.each(Object.entries(CFG_KEYS))('%s follows the scheme and round-trips', (_name, spec) => {
    expect(spec.key).toMatch(SCHEME);
    expect(cfgStorage.write(spec.key, 'v', spec.store)).toBe(true);
    expect(cfgStorage.read(spec.key, spec.store)).toBe('v');
    cfgStorage.remove(spec.key, spec.store);
    expect(cfgStorage.read(spec.key, spec.store)).toBeNull();
  });

  it('has no duplicate key within one store', () => {
    const seen = new Set<string>();
    for (const spec of Object.values(CFG_KEYS)) {
      const id = `${spec.store}:${spec.key}`;
      expect(seen.has(id)).toBe(false);
      seen.add(id);
    }
  });

  it.each(Object.entries(CFG_FAMILIES))('family %s prefix follows the scheme', (_name, family) => {
    expect(family.prefix).toMatch(/^cfg(\.[a-z0-9_]+)+\.$/);
    expect(cfgStorage.familyKey(family, 'Room 1/A')).toBe(`${family.prefix}room_1_a`);
  });

  it('does not read old spellings', () => {
    localStorage.setItem('cfg.access_token', 'old');
    expect(cfgStorage.read(CFG_KEYS.accessToken.key)).toBeNull();
  });
});

describe('validation', () => {
  it('rejects keys outside the scheme', () => {
    for (const bad of ['auth_email', 'cfg', 'cfg.', 'cfg.Auth.x', 'cfg.auth-x', 'other.x']) {
      expect(() => cfgStorage.read(bad)).toThrow(TypeError);
    }
  });

  it('app storage reads cfg and own keys, writes only its own', () => {
    const app = createStorage('kino');
    expect(app.isValid('kino.player.volume')).toBe(true);
    expect(app.isValid('cfg.auth.email')).toBe(true);
    expect(app.isValid('other.x')).toBe(false);
    expect(() => app.write('cfg.auth.email', 'x')).toThrow(TypeError);
    expect(app.write('kino.player.volume', '3')).toBe(true);
    expect(app.read('kino.player.volume')).toBe('3');
  });

  it('builds and normalises keys from parts', () => {
    const app = createStorage('kino');
    expect(app.key('Player', 'Last Volume')).toBe('kino.player.last_volume');
    expect(() => app.key('player', '  ')).toThrow(TypeError);
    expect(() => createStorage('Bad-Owner')).toThrow(TypeError);
    expect(normalizeSegment(' A-b c ')).toBe('a_b_c');
  });
});

describe('guarded I/O', () => {
  it('keeps the value in memory when the browser refuses a write', () => {
    const spy = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new DOMException('full', 'QuotaExceededError');
    });
    expect(cfgStorage.write(CFG_KEYS.email.key, 'a@b.c')).toBe(false);
    expect(cfgStorage.read(CFG_KEYS.email.key)).toBe('a@b.c');
    spy.mockRestore();
  });

  it('survives a throwing storage getter', () => {
    const spy = vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
      throw new Error('denied');
    });
    expect(cfgStorage.read(CFG_KEYS.email.key)).toBeNull();
    spy.mockRestore();
  });

  it('readJSON returns null on garbage', () => {
    localStorage.setItem(CFG_KEYS.uiState.key, '{oops');
    expect(cfgStorage.readJSON(CFG_KEYS.uiState.key)).toBeNull();
    cfgStorage.writeJSON(CFG_KEYS.uiState.key, { a: 1 });
    expect(cfgStorage.readJSON(CFG_KEYS.uiState.key)).toEqual({ a: 1 });
  });
});

describe('clearAll', () => {
  it('removes personal keys and family members, keeps preferences', () => {
    cfgStorage.write(CFG_KEYS.accessToken.key, 't');
    cfgStorage.write(CFG_KEYS.chatSpeechLanguage.key, 'ru');
    cfgStorage.write(cfgStorage.familyKey(CFG_FAMILIES.chatDraft, 'r1'), 'draft', 'session');
    cfgStorage.write(cfgStorage.familyKey(CFG_FAMILIES.dataTree, 't1'), 'tree');
    cfgStorage.clearAll();
    expect(cfgStorage.read(CFG_KEYS.accessToken.key)).toBeNull();
    expect(cfgStorage.read(cfgStorage.familyKey(CFG_FAMILIES.chatDraft, 'r1'), 'session')).toBeNull();
    expect(cfgStorage.read(CFG_KEYS.chatSpeechLanguage.key)).toBe('ru');
    expect(cfgStorage.read(cfgStorage.familyKey(CFG_FAMILIES.dataTree, 't1'))).toBe('tree');
  });

  it('{ all: true } wipes the owner namespace but not foreign keys', () => {
    localStorage.setItem('NEXT_LOCALE', 'en');
    cfgStorage.write(CFG_KEYS.chatSpeechLanguage.key, 'ru');
    cfgStorage.write('cfg.custom.thing', '1');
    cfgStorage.clearAll({ all: true });
    expect(localStorage.getItem('cfg.custom.thing')).toBeNull();
    expect(localStorage.getItem('NEXT_LOCALE')).toBe('en');
  });
});

describe('cross-tab', () => {
  it('onChange fires for the key from another tab only', () => {
    const listener = vi.fn();
    const off = cfgStorage.onChange(CFG_KEYS.accessToken.key, listener);
    window.dispatchEvent(new StorageEvent('storage', { key: 'cfg.other.x', newValue: '1', storageArea: localStorage }));
    window.dispatchEvent(new StorageEvent('storage', { key: CFG_KEYS.accessToken.key, newValue: 'n', storageArea: sessionStorage }));
    expect(listener).not.toHaveBeenCalled();
    window.dispatchEvent(new StorageEvent('storage', { key: CFG_KEYS.accessToken.key, newValue: 'n', storageArea: localStorage }));
    expect(listener).toHaveBeenCalledWith('n');
    off();
    window.dispatchEvent(new StorageEvent('storage', { key: null, storageArea: localStorage }));
    expect(listener).toHaveBeenCalledTimes(1);
  });
});

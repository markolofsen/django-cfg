// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { CFG_KEYS } from '@djangocfg/api/storage';

const PREFS = CFG_KEYS.formsSpeechPrefs.key;
const SHARED = CFG_KEYS.chatSpeechLanguage.key;

async function load(): Promise<void> {
  vi.resetModules();
  await import('../store/prefsStore');
}

describe('legacy dictation language carry-over', () => {
  beforeEach(() => localStorage.clear());

  it('moves a pick made in the old prefs to the shared key and drops it from the blob', async () => {
    localStorage.setItem(PREFS, JSON.stringify({ state: { language: 'ru-RU', earcons: true }, version: 0 }));
    await load();
    expect(localStorage.getItem(SHARED)).toBe('ru-RU');
    expect(JSON.parse(localStorage.getItem(PREFS)!).state).toEqual({ earcons: true });
  });

  it('never overwrites a language already chosen in a chat', async () => {
    localStorage.setItem(SHARED, 'de-DE');
    localStorage.setItem(PREFS, JSON.stringify({ state: { language: 'ru-RU' }, version: 0 }));
    await load();
    expect(localStorage.getItem(SHARED)).toBe('de-DE');
  });

  it('leaves everything alone when there is nothing to carry over', async () => {
    await load();
    expect(localStorage.getItem(SHARED)).toBeNull();
  });
});

'use client';

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { CFG_KEYS } from '@djangocfg/api/storage';

export interface SpeechPrefs {
  deviceId: string | null;
  engineId: string | null;
  earcons: boolean;
  /**
   * Hold-to-record mode: press-and-hold the mic button records, release
   * stops (claude.ai-style). `false` (default) keeps the classic toggle
   * click. Surfaced as the switch row in `<VoiceControlMenu>`.
   */
  holdToRecord: boolean;
}

const DEFAULTS: SpeechPrefs = {
  deviceId: null,
  engineId: null,
  earcons: false,
  holdToRecord: false,
};

interface PrefsStore extends SpeechPrefs {
  setDeviceId: (v: string | null) => void;
  setEngineId: (v: string | null) => void;
  setEarcons: (v: boolean) => void;
  setHoldToRecord: (v: boolean) => void;
  reset: () => void;
}

/**
 * One-time carry-over: before the dictation language became ONE value shared
 * with every chat (`cfg.chat.speech_language`), it was stored inside these
 * prefs. A pick made then moves to the shared key (unless one is already there)
 * and leaves the old blob, so nobody has to choose again. Runs once at import,
 * i.e. before any hook reads the shared key on mount.
 */
function migrateLegacyLanguage(): void {
  if (typeof window === 'undefined') return;
  try {
    const raw = window.localStorage.getItem(CFG_KEYS.formsSpeechPrefs.key);
    if (raw === null) return;
    const blob = JSON.parse(raw) as { state?: { language?: unknown } };
    const legacy = blob?.state?.language;
    if (!blob?.state || !('language' in blob.state)) return;
    if (
      typeof legacy === 'string' &&
      legacy !== '' &&
      window.localStorage.getItem(CFG_KEYS.chatSpeechLanguage.key) === null
    ) {
      window.localStorage.setItem(CFG_KEYS.chatSpeechLanguage.key, legacy);
    }
    delete blob.state.language;
    window.localStorage.setItem(CFG_KEYS.formsSpeechPrefs.key, JSON.stringify(blob));
  } catch {
    // Storage blocked or the blob is not ours: nothing to carry over.
  }
}

migrateLegacyLanguage();

export const useSpeechPrefs = create<PrefsStore>()(
  persist(
    (set) => ({
      ...DEFAULTS,
      setDeviceId: (deviceId) => set({ deviceId }),
      setEngineId: (engineId) => set({ engineId }),
      setEarcons: (earcons) => set({ earcons }),
      setHoldToRecord: (holdToRecord) => set({ holdToRecord }),
      reset: () => set({ ...DEFAULTS }),
    }),
    {
      name: CFG_KEYS.formsSpeechPrefs.key,
      storage: createJSONStorage(() =>
        typeof window === 'undefined'
          ? (undefined as unknown as Storage)
          : window.localStorage,
      ),
    },
  ),
);

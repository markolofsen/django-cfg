'use client';

import { useSpeechPrefs } from '../store/prefsStore';
import type { SpeechPrefs } from '../store/prefsStore';

/** Thin selector hook so consumers can subscribe to prefs without pulling the whole zustand store. */
export function useEnginePrefs(): SpeechPrefs & {
  setDeviceId: (v: string | null) => void;
  setEngineId: (v: string | null) => void;
  setEarcons: (v: boolean) => void;
  reset: () => void;
} {
  return useSpeechPrefs();
}

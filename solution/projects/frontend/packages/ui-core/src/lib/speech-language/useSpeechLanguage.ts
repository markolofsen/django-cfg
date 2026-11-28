"use client";

import { useCallback, useMemo } from "react";

import { CFG_KEYS } from "@djangocfg/api/storage";

import { useBrowserLanguages } from "../../hooks/device/useBrowserLanguages";
import { useLocalStorage } from "../../hooks/storage/useLocalStorage";
import { resolveLanguage } from "./resolve";

/**
 * Which language dictation listens for, and how it is remembered. ONE answer for
 * every dictation surface (chats, a composer, a form field), wherever it is
 * embedded.
 *
 * A language is a property of the SPEAKER, not of the surface they are in, so the
 * pick is global. It lives in `localStorage` under one key and is read through
 * `useLocalStorage`, whose same-tab registry and `storage` event make a change
 * in one place visible in all the others at once, without a reload. An empty
 * value means "not picked": the language is then guessed from the browser
 * (`resolveLanguage`).
 */
const STORAGE_KEY = CFG_KEYS.chatSpeechLanguage.key;

export interface UseSpeechLanguageResult {
  /** The BCP-47 speech tag in force. Never empty. */
  readonly language: string;
  /** Whether the user chose it, as opposed to it being guessed for them. */
  readonly explicit: boolean;
  readonly setLanguage: (tag: string) => void;
  /** Forget the pick and go back to guessing. */
  readonly clear: () => void;
}

export interface SpeechLanguageOptions {
  /**
   * The host UI's locale (`ru`). A TIE-BREAKER, never the source: it counts only
   * when the browser also lists that language as spoken, so an English app on a
   * browser that lists Russian can dictate Russian and the reverse holds too.
   */
  readonly uiLocale?: string | undefined;
}

export function useSpeechLanguage(options: SpeechLanguageOptions = {}): UseSpeechLanguageResult {
  const [stored, setStored, removeStored] = useLocalStorage<string>(STORAGE_KEY, "");
  const browser = useBrowserLanguages();
  const picked = stored === "" ? undefined : stored;

  const language = useMemo(
    () =>
      resolveLanguage({
        picked,
        uiLocale: options.uiLocale,
        browserLanguages: browser.languages,
        browserLanguage: browser.primary,
        intlLocale: browser.intl,
      }),
    [picked, options.uiLocale, browser],
  );

  const setLanguage = useCallback((tag: string) => setStored(tag), [setStored]);
  const clear = useCallback(() => removeStored(), [removeStored]);

  return useMemo(
    () => ({ language, explicit: picked !== undefined, setLanguage, clear }),
    [language, picked, setLanguage, clear],
  );
}

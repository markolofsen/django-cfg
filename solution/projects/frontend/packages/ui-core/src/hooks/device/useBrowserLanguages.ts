'use client';

import { useSyncExternalStore } from 'react';

/** What the browser says about the reader's languages. */
export interface BrowserLanguages {
  /** `navigator.languages` in the browser's own order (`navigator.language` alone when the list is empty). Empty on the server and on the first client render. */
  languages: readonly string[]
  /** `navigator.language`, or `undefined` where there is none. */
  primary: string | undefined
  /** The locale the runtime formats dates with (`Intl`), taken from the OS region/language settings. A weak extra signal when `languages` says nothing usable. */
  intl: string | undefined
}

const EMPTY: BrowserLanguages = { languages: [], primary: undefined, intl: undefined };

let cached: BrowserLanguages = EMPTY;
let cachedKey = '';

function snapshot(): BrowserLanguages {
  if (typeof navigator === 'undefined') return EMPTY;
  const languages = navigator.languages?.length ? [...navigator.languages] : navigator.language ? [navigator.language] : [];
  let intl: string | undefined;
  try {
    intl = Intl.DateTimeFormat().resolvedOptions().locale || undefined;
  } catch {
    intl = undefined;
  }
  const key = `${languages.join(',')}|${navigator.language ?? ''}|${intl ?? ''}`;
  // useSyncExternalStore needs the SAME object while nothing changed, or it loops.
  if (key !== cachedKey) {
    cachedKey = key;
    cached = { languages, primary: navigator.language || undefined, intl };
  }
  return cached;
}

function subscribe(onChange: () => void): () => void {
  window.addEventListener('languagechange', onChange);
  return () => window.removeEventListener('languagechange', onChange);
}

/**
 * The reader's languages as the browser reports them, kept current on `languagechange`.
 * Raw tags, not a decision: what to do with them (speech, translation, a default
 * locale) belongs to the caller, which knows which tags it supports.
 *
 * SSR-safe: the server and the first client render both see empty values, so
 * nothing mismatches on hydration; the real values arrive right after.
 *
 * @example
 * const { languages } = useBrowserLanguages()
 * const first = languages.find((tag) => supported.has(tag.split('-')[0]))
 */
export function useBrowserLanguages(): BrowserLanguages {
  return useSyncExternalStore(subscribe, snapshot, () => EMPTY);
}

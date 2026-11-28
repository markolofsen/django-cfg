'use client';

import { useLocaleOptional } from '@djangocfg/i18n';

import { toSpeechTag, useSpeechLanguage } from '@djangocfg/ui-core/lib/speech-language';

/**
 * Resolves the BCP-47 language tag a speech session should use.
 *
 * Priority: explicit prop → the user's pick (shared with every chat and
 * dictation field: `useSpeechLanguage` of ui-core) → a guess from the browser
 * (`navigator.languages`, then `Intl`) → `en-US`.
 *
 * The app locale only breaks a tie the browser already allows: UI language is
 * not speech language. A Russian speaker using an English UI still runs a
 * `ru-RU` browser, and dictation must understand what they actually speak with
 * zero configuration.
 *
 * Uses `useLocaleOptional` (not `useLocale`) so that an unmounted
 * provider doesn't silently inject `'en'`.
 */
export function useResolvedLanguage(explicit?: string): string {
  const locale = useLocaleOptional();
  const shared = useSpeechLanguage({ uiLocale: locale ?? undefined });
  return toSpeechTag(explicit) ?? shared.language;
}

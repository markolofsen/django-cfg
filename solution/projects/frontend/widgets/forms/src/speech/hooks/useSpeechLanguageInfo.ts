'use client';

import { useMemo } from 'react';

import {
  countryFromTag,
  findSpeechLanguage,
  useSpeechLanguage,
} from '@djangocfg/ui-core/lib/speech-language';
import { useResolvedLanguage } from './useResolvedLanguage';

export interface SpeechLanguageInfo {
  /**
   * BCP-47 tag that `useSpeechRecognition` will actually pass to the
   * engine right now. Always non-null (falls through `prefs →
   * navigator → i18n → 'en-US'`).
   */
  tag: string;
  /**
   * ISO-639 primary subtag of `tag` (`ru`, `en`, `cmn`). Useful as a
   * map key when the host wires its own per-language behaviour
   * (avatars, copy variants, etc.).
   */
  iso: string;
  /**
   * ISO-3166 alpha-2 country code extracted from `tag` (`RU`, `US`,
   * `CN`). `null` when the tag has no region subtag — rare for our
   * catalogue (every entry ships at least one regional dialect) but
   * possible for custom-engine tags supplied by hosts.
   */
  country: string | null;
  /**
   * Native-script language name (`'Русский'`, `'中文'`). `null` for
   * tags outside our catalogue.
   */
  name: string | null;
  /**
   * Lowercase English name (`'russian'`, `'chinese'`). `null` for
   * tags outside our catalogue. Handy for analytics or English-only
   * UI surfaces.
   */
  englishName: string | null;
  /**
   * Region label for the current dialect (`'Russia'`, `'United
   * Kingdom'`, `'香港'`). `null` for unknown tags.
   */
  region: string | null;
  /**
   * `true` iff the user explicitly picked a language via
   * `<ChatHeaderLanguageButton>` / `useSpeechPrefs.setLanguage(...)`.
   * `false` means the resolved tag came from a lower-priority source
   * (i18n locale, `navigator.language`, default).
   *
   * Use this when you want to distinguish "user told us to use ru-RU"
   * from "we guessed ru-RU from browser headers". Analytics often
   * cares about that distinction.
   */
  hasUserChoice: boolean;
}

/**
 * One-shot read of "what speech language is active right now and why".
 *
 * Pulls together `useResolvedLanguage`, `useSpeechPrefs.language`, and
 * the static catalogue (`findSpeechLanguage` / `countryFromTag`) into
 * a single memoised object so consumers don't have to compose them by
 * hand for every header badge / analytics call / persisted-state push.
 *
 * Reactive: re-renders when the user picks a different language in
 * the chat header, when i18n locale changes, or when the underlying
 * `navigator.language` reading flips (mount-time only).
 *
 * @example Render a status badge somewhere in the app shell
 * ```tsx
 * const { tag, name, country } = useSpeechLanguageInfo();
 * return (
 *   <Badge>
 *     <Flag countryCode={country} />
 *     {name ?? tag}
 *   </Badge>
 * );
 * ```
 *
 * @example Sync the user's STT pick to a backend setting
 * ```tsx
 * const { tag, hasUserChoice } = useSpeechLanguageInfo();
 * useEffect(() => {
 *   if (!hasUserChoice) return;             // skip auto-resolved values
 *   void api.user.update({ speechLanguage: tag });
 * }, [tag, hasUserChoice]);
 * ```
 */
export function useSpeechLanguageInfo(): SpeechLanguageInfo {
  const { explicit } = useSpeechLanguage();
  const tag = useResolvedLanguage();
  return useMemo<SpeechLanguageInfo>(() => {
    const found = findSpeechLanguage(tag);
    return {
      tag,
      iso: found?.language.iso ?? (tag.split('-')[0] ?? tag).toLowerCase(),
      country: countryFromTag(tag),
      name: found?.language.name ?? null,
      englishName: found?.language.englishName ?? null,
      region: found?.dialect.region ?? null,
      hasUserChoice: explicit,
    };
  }, [tag, explicit]);
}

'use client';

import { useEffect, useMemo, useState } from 'react';

import { useBrowserLanguages, useLocation } from '@djangocfg/ui-core/hooks';

import type { I18nLayoutConfig } from '../../layouts/types/layout.types';
import { useLayoutI18nOptional } from '../../shared/LayoutI18nProvider';
import {
  decideSuggestion,
  dismissPair,
  isAutomated,
  isExcludedPath,
  reconcileMemory,
  suggestLocale,
} from './decide';
import { readMemory, writeMemory } from './memory';
import { LocaleSuggestionView } from './LocaleSuggestionView';

export const DEFAULT_DELAY_MS = 1500;

/**
 * Offers the visitor the site's language they browse in, once, quietly.
 * Mounted by `BaseApp`; reads `i18n` from the layout context, so an app needs no setup.
 * Renders nothing on the server and on the first client render (no hydration difference), nothing for
 * one-language sites, crawlers and automation, and nothing until the page has settled for `delayMs`.
 */
export function LocaleSuggestion() {
  const i18n = useLayoutI18nOptional();
  // First check, before any hook that subscribes or reads storage: fewer than two locales, or switched off, mounts nothing.
  if (!i18n || i18n.suggestion === false || i18n.locales.length < 2) return null;
  return <LocaleSuggestionHost i18n={i18n} />;
}

function LocaleSuggestionHost({ i18n }: { i18n: I18nLayoutConfig }) {
  const { languages } = useBrowserLanguages();
  const { pathname } = useLocation();
  const [settled, setSettled] = useState(false);
  const [target, setTarget] = useState<string | null>(null);

  const option = i18n?.suggestion;
  const enabled = option !== false;
  const options = option === false || option === undefined ? undefined : option;
  const delayMs = options?.delayMs ?? DEFAULT_DELAY_MS;
  const ttlDays = options?.ttlDays;
  const exclude = options?.exclude;
  const current = i18n?.locale;
  const siteLocales = i18n?.locales;
  const localesKey = siteLocales?.join(',') ?? '';
  const languagesKey = languages.join(',');
  const eligible = enabled && !!current && (siteLocales?.length ?? 0) > 1 && languages.length > 0;

  // The page must be visible and quiet for `delayMs` before anything appears.
  useEffect(() => {
    if (!eligible) return;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const start = () => {
      timer = setTimeout(() => setSettled(true), delayMs);
    };
    const onVisible = () => {
      if (!document.hidden) {
        document.removeEventListener('visibilitychange', onVisible);
        start();
      }
    };
    if (document.hidden) document.addEventListener('visibilitychange', onVisible);
    else start();
    return () => {
      clearTimeout(timer);
      document.removeEventListener('visibilitychange', onVisible);
    };
  }, [eligible, delayMs]);

  // Decide once per (languages, locale): record the page view, then ask the pure rule.
  useEffect(() => {
    if (!eligible || !current || !siteLocales) {
      setTarget(null);
      return;
    }
    if (isAutomated(navigator.userAgent, navigator.webdriver)) {
      setTarget(null);
      return;
    }
    const now = Date.now();
    const input = { browserLanguages: languages, siteLocales, current, ttlDays };
    const memory = reconcileMemory(readMemory(), { current, candidate: suggestLocale(input), now, ttlDays });
    writeMemory(memory);
    setTarget(decideSuggestion({ ...input, memory, now }));
    // `languages` and `siteLocales` are keyed by their content: a new array with the same tags must not re-run this.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [eligible, current, languagesKey, localesKey, ttlDays]);

  const excluded = useMemo(() => isExcludedPath(pathname, exclude), [pathname, exclude]);

  if (!settled || !target || excluded) return null;
  const browserLanguage = languages[0] ?? target;

  const close = () => {
    writeMemory(dismissPair(readMemory(), target, i18n.locale, Date.now()));
    setTarget(null);
  };

  return (
    <LocaleSuggestionView
      browserLanguage={browserLanguage}
      target={target}
      onSwitch={() => {
        setTarget(null);
        i18n.onLocaleChange(target);
      }}
      onDismiss={close}
    />
  );
}

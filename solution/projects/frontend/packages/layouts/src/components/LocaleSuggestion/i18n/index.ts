'use client';

import { createCopy, type Locale } from '@djangocfg/i18n/copy';

import { ar } from './locales/ar';
import { da } from './locales/da';
import { de } from './locales/de';
import { en } from './locales/en';
import { es } from './locales/es';
import { fr } from './locales/fr';
import { it } from './locales/it';
import { ja } from './locales/ja';
import { ko } from './locales/ko';
import { nl } from './locales/nl';
import { no } from './locales/no';
import { pl } from './locales/pl';
import { ptBR } from './locales/ptBR';
import { ru } from './locales/ru';
import { sv } from './locales/sv';
import { tr } from './locales/tr';
import { zh } from './locales/zh';

import type { LocaleSuggestionCopy } from './types';

export type { LocaleSuggestionCopy } from './types';
export { fill } from '@djangocfg/i18n/copy';

/** Every bundled dictionary, typed complete over the shared `Locale` union. */
export const LOCALE_SUGGESTION_DICTIONARIES: Readonly<Record<Locale, LocaleSuggestionCopy>> = {
  en, ru, ko, ja, de, fr, zh, it, es, nl, ar, tr, pl, sv, no, da,
  'pt-BR': ptBR,
};

/**
 * The hint speaks the VISITOR's language, not the page's: `useLocaleSuggestionCopy(browserTag)`.
 * A tag with no bundled dictionary resolves to English.
 */
export const useLocaleSuggestionCopy = createCopy(LOCALE_SUGGESTION_DICTIONARIES).useCopy;

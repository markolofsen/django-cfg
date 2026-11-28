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
import { ptBR } from './locales/pt-BR';
import { ru } from './locales/ru';
import { sv } from './locales/sv';
import { tr } from './locales/tr';
import { zh } from './locales/zh';
import type { AssistantCopy } from './types';

export type { AssistantCopy, SessionNotice } from './types';

/** Every bundled dictionary, typed complete over the shared `Locale` union. */
export const ASSISTANT_DICTIONARIES: Readonly<Record<Locale, AssistantCopy>> = {
  en, ru, ko, ja, de, fr, zh, it, es, nl, ar, tr, pl, sv, no, da,
  'pt-BR': ptBR,
};

const kit = createCopy(ASSISTANT_DICTIONARIES);

/**
 * The assistant's own words for the active language: the `locale` prop, else the
 * `@djangocfg/i18n` provider, else English. The host passes no strings.
 */
export const useAssistantCopy = kit.useCopy;

/** The bundled locale the assistant resolved to (feed it to `Intl`). */
export const useAssistantLocale = kit.useLocale;

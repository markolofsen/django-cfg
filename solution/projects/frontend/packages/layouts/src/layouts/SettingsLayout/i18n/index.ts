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

import type { SettingsCopy } from './types';

export type { SettingsCopy } from './types';
export { fill } from '@djangocfg/i18n/copy';

/** Every bundled dictionary, typed complete over the shared `Locale` union. */
export const SETTINGS_DICTIONARIES: Readonly<Record<Locale, SettingsCopy>> = {
  en, ru, ko, ja, de, fr, zh, it, es, nl, ar, tr, pl, sv, no, da,
  'pt-BR': ptBR,
};

/** Settings copy for the active language: the `@djangocfg/i18n` provider, else English. */
const kit = createCopy(SETTINGS_DICTIONARIES);
export const useSettingsCopy = kit.useCopy;

/** The bundled locale `useSettingsCopy` resolved to, for date formatting. */
export const useSettingsLocale = kit.useLocale;

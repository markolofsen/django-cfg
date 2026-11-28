'use client';

import { useMemo } from 'react';

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

import type { MediaCopy } from './types';

export type { MediaCopy } from './types';

/** Every bundled dictionary, typed complete over the shared `Locale` union. */
export const MEDIA_DICTIONARIES: Readonly<Record<Locale, MediaCopy>> = {
  en, ru, ko, ja, de, fr, zh, it, es, nl, ar, tr, pl, sv, no, da,
  'pt-BR': ptBR,
};

/** English, for a host that wants the unlocalised defaults. */
export const DEFAULT_MEDIA_COPY: MediaCopy = en;

const kit = createCopy(MEDIA_DICTIONARIES);

/**
 * The copy a component renders: the dictionary for the active language (the
 * `locale` argument, else the `@djangocfg/i18n` provider, else English), with
 * the host's partial override on top. A host that overrides one string does
 * not blank the other fourteen.
 */
export function useMediaCopy(copy?: Partial<MediaCopy>, locale?: string): MediaCopy {
  const base = kit.useCopy(locale);
  return useMemo(() => (copy ? { ...base, ...copy } : base), [base, copy]);
}

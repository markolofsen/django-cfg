'use client';

import { Fragment, type ReactNode } from 'react';

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

import type { McpCopy } from './types';

export type { McpConnectCopy, McpConsentCopy, McpCopy, McpRenewCopy } from './types';

/** Every bundled dictionary, typed complete over the shared `Locale` union. */
export const MCP_DICTIONARIES: Readonly<Record<Locale, McpCopy>> = {
  en, ru, ko, ja, de, fr, zh, it, es, nl, ar, tr, pl, sv, no, da,
  'pt-BR': ptBR,
};

const kit = createCopy(MCP_DICTIONARIES);

/**
 * The copy for the active language: the `locale` prop, else the
 * `@djangocfg/i18n` provider, else English (a story, a test).
 */
export const useMcpCopy = kit.useCopy;

/** The bundled locale `useMcpCopy` resolved to, for number and date formatting. */
export const useMcpLocale = kit.useLocale;

/** `{name}` placeholders replaced by nodes, so a value can be bold in any word order. */
export function fill(template: string, values: Record<string, ReactNode>): ReactNode[] {
  return template.split(/\{(\w+)\}/).map((part, i) =>
    i % 2 === 1 ? <Fragment key={i}>{values[part] ?? `{${part}}`}</Fragment> : part,
  );
}

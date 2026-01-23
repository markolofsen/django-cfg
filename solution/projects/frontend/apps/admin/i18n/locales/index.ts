/**
 * Admin Locales Index
 *
 * Re-exports all admin locale translations
 */

export { en, type AdminTranslations } from './en';
export { ko } from './ko';
export { ru } from './ru';

// Consolidated locales object for easy access
import { en } from './en';
import { ko } from './ko';
import { ru } from './ru';

export const adminLocales = {
  en,
  ko,
  ru,
} as const;

export type AdminLocaleKey = keyof typeof adminLocales;

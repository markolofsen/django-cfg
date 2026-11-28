/**
 * i18n Types for Next.js App Router
 *
 * Integrates next-intl with @djangocfg/i18n
 */

import type { LocaleCode, I18nTranslations } from '@djangocfg/i18n';

// ─────────────────────────────────────────────────────────────────────────────
// Configuration Types
// ─────────────────────────────────────────────────────────────────────────────

export interface I18nConfig {
  /** Supported locales */
  locales: LocaleCode[];
  /** Default locale (fallback) */
  defaultLocale: LocaleCode;
  /** Locale prefix strategy */
  localePrefix?: 'always' | 'as-needed' | 'never';
  /** Cookie name for locale preference */
  cookieName?: string;
  /** Paths to exclude from locale routing (e.g., '/api', '/_next') */
  excludedPaths?: string[];
}

export interface I18nPluginOptions extends I18nConfig {
  /** Path to i18n request config file (default: './src/i18n/request.ts' or './i18n/request.ts') */
  requestConfig?: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Translation Types
// ─────────────────────────────────────────────────────────────────────────────

/** Messages structure - compatible with next-intl */
export type Messages = I18nTranslations & {
  [namespace: string]: Record<string, unknown>;
};

/** Locale-specific messages loader */
export type MessagesLoader = (locale: LocaleCode) => Promise<Messages> | Messages;

/** Extension translations that can be merged */
export interface ExtensionMessages {
  namespace: string;
  messages: Record<LocaleCode, Record<string, unknown>>;
}

// ─────────────────────────────────────────────────────────────────────────────
// Provider Types
// ─────────────────────────────────────────────────────────────────────────────

export interface I18nProviderProps {
  /** Current locale */
  locale: LocaleCode;
  /** Translation messages */
  messages: Messages;
  /**
   * Locales the app ships. `useLocales()` / `useLocaleSwitcher()` report these;
   * without it they fall back to the package's built-in list.
   */
  locales?: LocaleCode[];
  /** Time zone for date/time formatting */
  timeZone?: string;
  /** Now value for relative time */
  now?: Date;
  /** Children */
  children: React.ReactNode;
}

// ─────────────────────────────────────────────────────────────────────────────
// Routing Types
// ─────────────────────────────────────────────────────────────────────────────

export interface LocaleParams {
  locale: string;
}

export interface LocaleLayoutProps {
  children: React.ReactNode;
  params: Promise<LocaleParams>;
}

export interface LocalePageProps {
  params: Promise<LocaleParams>;
  searchParams?: Promise<Record<string, string | string[] | undefined>>;
}

// ─────────────────────────────────────────────────────────────────────────────
// Re-exports from @djangocfg/i18n
// ─────────────────────────────────────────────────────────────────────────────

export type { LocaleCode, I18nTranslations } from '@djangocfg/i18n';

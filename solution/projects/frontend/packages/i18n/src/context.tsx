'use client'

import * as React from 'react'

import { en } from './locales/en'
import type {
  I18nContextValue,
  I18nProviderProps,
  I18nTranslations,
  LocaleCode,
} from './types'
import { getNestedValue, interpolate, mergeTranslations } from './utils'

/**
 * I18n Context
 */
const I18nContext = React.createContext<I18nContextValue | null>(null)

/**
 * Default translations (English)
 */
const defaultTranslations: I18nTranslations = en

/**
 * I18n Provider
 *
 * @example
 * // Basic usage with single locale
 * import { I18nProvider, ru } from '@djangocfg/i18n'
 *
 * <I18nProvider locale="ru" translations={ru}>
 *   <App />
 * </I18nProvider>
 *
 * @example
 * // With all translations for dynamic switching
 * import { I18nProvider, en, ru, ko } from '@djangocfg/i18n'
 *
 * <I18nProvider
 *   locale={currentLocale}
 *   allTranslations={{ en, ru, ko }}
 *   onLocaleChange={(locale) => setCurrentLocale(locale)}
 * >
 *   <App />
 * </I18nProvider>
 *
 * @example
 * // With custom overrides
 * import { I18nProvider, ru, mergeTranslations } from '@djangocfg/i18n'
 *
 * const customRu = mergeTranslations(ru, {
 *   ui: { select: { placeholder: 'Выберите марку...' } }
 * })
 *
 * <I18nProvider locale="ru" translations={customRu}>
 *   <App />
 * </I18nProvider>
 */
export function I18nProvider({
  children,
  locale: initialLocale = 'en',
  translations: initialTranslations,
  allTranslations,
  onLocaleChange,
}: I18nProviderProps) {
  const [locale, setLocaleState] = React.useState<LocaleCode>(initialLocale)

  // Resolve current translations
  const translations = React.useMemo<I18nTranslations>(() => {
    // If allTranslations provided, use it to get translations for current locale
    if (allTranslations && allTranslations[locale]) {
      const localeTranslations = allTranslations[locale]
      // Merge with defaults to fill any missing keys
      return mergeTranslations(defaultTranslations, localeTranslations)
    }

    // If single translations provided, use them
    if (initialTranslations) {
      return mergeTranslations(
        defaultTranslations,
        initialTranslations as I18nTranslations
      )
    }

    // Fallback to defaults
    return defaultTranslations
  }, [locale, allTranslations, initialTranslations])

  // Translation function
  const t = React.useCallback(
    (key: string, params?: Record<string, string | number>): string => {
      const value = getNestedValue(
        translations as unknown as Record<string, unknown>,
        key
      )

      if (value === undefined) {
        // Development warning
        if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
          console.warn(`[i18n] Missing translation key: "${key}"`)
        }
        // Return the key as fallback
        return key
      }

      return interpolate(value, params)
    },
    [translations]
  )

  // Locale change handler
  const setLocale = React.useCallback(
    (newLocale: LocaleCode) => {
      setLocaleState(newLocale)
      onLocaleChange?.(newLocale)
    },
    [onLocaleChange]
  )

  // Sync with external locale changes.
  //
  // The comparison moved inside the updater rather than `locale` joining the
  // deps: this effect must run when the PROP changes, not when local state
  // does. Depending on `locale` would re-run it after every `setLocale` call
  // and reset the user's choice back to `initialLocale`.
  React.useEffect(() => {
    setLocaleState((current) => (current === initialLocale ? current : initialLocale))
  }, [initialLocale])

  const value = React.useMemo<I18nContextValue>(
    () => ({
      locale,
      translations,
      t,
      setLocale,
    }),
    [locale, translations, t, setLocale]
  )

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}

/**
 * Hook to access i18n context
 *
 * @example
 * function MyComponent() {
 *   const { t, locale, setLocale } = useI18n()
 *
 *   return (
 *     <div>
 *       <p>{t('ui.select.placeholder')}</p>
 *       <p>{t('ui.pagination.showing', { from: 1, to: 10, total: 100 })}</p>
 *       <button onClick={() => setLocale('ru')}>Switch to Russian</button>
 *     </div>
 *   )
 * }
 */
export function useI18n(): I18nContextValue {
  const context = React.useContext(I18nContext)

  if (!context) {
    // Return default implementation if no provider
    // This allows components to work without provider (using English defaults)
    return {
      locale: 'en',
      translations: defaultTranslations,
      t: (key: string, params?: Record<string, string | number>) => {
        const value = getNestedValue(
          defaultTranslations as unknown as Record<string, unknown>,
          key
        )
        if (value === undefined) return key
        return interpolate(value, params)
      },
      setLocale: () => {
        if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
          console.warn(
            '[i18n] setLocale called but no I18nProvider found. Wrap your app with I18nProvider to enable locale switching.'
          )
        }
      },
    }
  }

  return context
}

/**
 * Hook to get the translation function only
 * Useful when you only need translations without other context values
 *
 * @example
 * function MyComponent() {
 *   const t = useTranslation()
 *   return <span>{t('ui.form.save')}</span>
 * }
 */
export function useTranslation() {
  const { t } = useI18n()
  return t
}

/**
 * Hook to get current locale
 *
 * @example
 * function MyComponent() {
 *   const locale = useLocale()
 *   return <span>Current: {locale}</span>
 * }
 */
export function useLocale(): LocaleCode {
  const { locale } = useI18n()
  return locale
}

/**
 * Like `useLocale()`, but returns `null` when no `<I18nProvider>` is
 * mounted instead of falling back to `'en'`. Useful for code that
 * needs to distinguish "no app locale at all" from "app locale is en"
 * — e.g. speech recognition's `auto` mode wants to fall through to
 * `navigator.language` when the app hasn't set one.
 */
export function useLocaleOptional(): LocaleCode | null {
  const context = React.useContext(I18nContext)
  return context?.locale ?? null
}

/**
 * Alias for useTranslation
 * Lightweight hook that just returns the t function
 * Works with or without I18nProvider (falls back to English)
 *
 * @example
 * function MyComponent() {
 *   const t = useT()
 *   return <span>{t('ui.form.save')}</span>
 * }
 */
export const useT = useTranslation

/**
 * Type-safe translation hook
 *
 * Returns a translation function that only accepts valid keys from your translations type.
 * Use this when you want compile-time checking of translation keys.
 *
 * @example
 * ```typescript
 * import { useTypedT } from '@djangocfg/i18n'
 * import type { I18nTranslations } from '@djangocfg/i18n'
 *
 * function MyComponent() {
 *   const t = useTypedT<I18nTranslations>()
 *   return <span>{t('ui.form.save')}</span> // OK
 *   return <span>{t('ui.form.typo')}</span> // Compile error!
 * }
 * ```
 *
 * @example
 * ```typescript
 * // With merged translations (app + extensions)
 * import type { AppTranslations } from '@/i18n/types'
 *
 * function MyComponent() {
 *   const t = useTypedT<AppTranslations>()
 *   return <span>{t('leads.form.title')}</span> // OK if leads is in AppTranslations
 * }
 * ```
 */
export function useTypedT<T extends object>(): (
  key: import('./utils/path-keys').PathKeys<T>,
  params?: Record<string, string | number>
) => string {
  const { t } = useI18n()
  return t as (
    key: import('./utils/path-keys').PathKeys<T>,
    params?: Record<string, string | number>
  ) => string
}

/**
 * Get translation without hook (for class components or non-React contexts)
 * Always uses English defaults, no context support
 *
 * @example
 * // In a class component
 * render() {
 *   const title = getT('layouts.errors.somethingWentWrong')
 *   return <h1>{title}</h1>
 * }
 *
 * @example
 * // With interpolation
 * const message = getT('ui.pagination.showing', { from: 1, to: 10, total: 100 })
 */
export function getT(
  key: string,
  params?: Record<string, string | number>
): string {
  const value = getNestedValue(
    defaultTranslations as unknown as Record<string, unknown>,
    key
  )
  if (value === undefined) return key
  return interpolate(value, params)
}

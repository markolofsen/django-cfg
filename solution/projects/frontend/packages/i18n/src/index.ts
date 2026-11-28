// Context & Hooks
export { I18nProvider, useI18n, useTranslation, useLocale, useLocaleOptional, useT, useTypedT, getT } from './context'

// Convenience: pre-typed hook for built-in I18nTranslations — no generic needed
// Usage: const t = useAppT()  instead of  const t = useTypedT<I18nTranslations>()
import { useTypedT } from './context'
import type { I18nTranslations } from './types'
export const useAppT = () => useTypedT<I18nTranslations>()

// Types
export type {
  I18nTranslations,
  PartialTranslations,
  LocaleCode,
  I18nContextValue,
  I18nProviderProps,
  DeepPartial,
  I18nKeys,
  I18nTranslationFn,
} from './types'

// Type-safe keys utilities
export type {
  PathKeys,
  TranslationFn,
  TypedTranslationFn,
  TranslationKeys,
  NestedKeyOf,
  NestedValueOf,
  NamespaceKeys,
  MessageKeys,
  IntlTranslator,
} from './utils/path-keys'

// Locales
export { en, ru, ko } from './locales'

// Utils
export { interpolate, mergeTranslations, createTranslations } from './utils'

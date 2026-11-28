/**
 * Type-safe translation keys
 *
 * Generates a union of all possible dot-notation paths from a nested object type.
 *
 * @example
 * ```typescript
 * type Translations = {
 *   ui: {
 *     form: { save: string; cancel: string }
 *     select: { placeholder: string }
 *   }
 * }
 *
 * type Keys = PathKeys<Translations>
 * // = "ui.form.save" | "ui.form.cancel" | "ui.select.placeholder"
 * ```
 */

/**
 * Recursively generates dot-notation paths for nested object types
 *
 * - For leaf values (string), returns the accumulated path
 * - For nested objects, recursively builds paths
 * - Limits depth to prevent infinite recursion with circular types
 */
export type PathKeys<T, Prefix extends string = '', Depth extends number[] = []> =
  // Limit recursion depth to 10 levels (prevents infinite types)
  Depth['length'] extends 10
    ? never
    : T extends string
      ? Prefix
      : T extends object
        ? {
            [K in keyof T & string]: PathKeys<
              T[K],
              Prefix extends '' ? K : `${Prefix}.${K}`,
              [...Depth, 0]
            >
          }[keyof T & string]
        : never

/**
 * Type-safe translation function signature
 *
 * @example
 * ```typescript
 * import type { TranslationFn, I18nTranslations } from '@djangocfg/i18n'
 *
 * // Type-safe t function
 * const t: TranslationFn<I18nTranslations> = useT()
 * t('ui.form.save') // OK
 * t('ui.form.typo') // Error: Argument of type '"ui.form.typo"' is not assignable
 * ```
 */
export type TranslationFn<T extends object> = {
  (key: PathKeys<T>, params?: Record<string, string | number>): string
}

/**
 * Creates a type-safe translation function type for a specific translations object
 *
 * @example
 * ```typescript
 * // In extension
 * import type { TypedTranslationFn } from '@djangocfg/i18n'
 * import type { LeadsTranslations } from './types'
 *
 * type LeadsT = TypedTranslationFn<{ leads: LeadsTranslations }>
 * ```
 */
export type TypedTranslationFn<T extends object> = TranslationFn<T>

/**
 * Extracts the keys type from a translations object
 *
 * @example
 * ```typescript
 * import type { TranslationKeys, I18nTranslations } from '@djangocfg/i18n'
 *
 * type Keys = TranslationKeys<I18nTranslations>
 * // = "ui.form.save" | "ui.select.placeholder" | ...
 * ```
 */
export type TranslationKeys<T extends object> = PathKeys<T>

// --- next-intl augmentation utilities ---
// Used in app global.d.ts to override useTranslations with type-safe keys.
// The standard use-intl AppConfig augmentation doesn't propagate through
// pnpm's nested node_modules, so apps override useTranslations directly.

/** All dot-separated paths (both leaves and namespaces) */
export type NestedKeyOf<T> = T extends object
  ? { [K in keyof T & string]: K | `${K}.${NestedKeyOf<T[K]>}` }[keyof T & string]
  : never

/** Resolve nested value by dot-separated path */
export type NestedValueOf<T, P extends string> = P extends `${infer K}.${infer R}`
  ? K extends keyof T ? NestedValueOf<T[K], R> : never
  : P extends keyof T ? T[P] : never

/** Paths that resolve to objects (valid useTranslations namespaces) */
export type NamespaceKeys<T, A extends string> = {
  [K in A]: NestedValueOf<T, K> extends string ? never : K
}[A]

/** Paths that resolve to strings (valid t() keys) */
export type MessageKeys<T, A extends string> = {
  [K in A]: NestedValueOf<T, K> extends string ? K : never
}[A]

/** Type-safe translator returned by useTranslations(namespace) */
export type IntlTranslator<Messages, NS extends NamespaceKeys<Messages, NestedKeyOf<Messages>>> = {
  <K extends MessageKeys<NestedValueOf<Messages, NS>, NestedKeyOf<NestedValueOf<Messages, NS>>>>(
    key: K,
    values?: Record<string, unknown>,
  ): string
  rich<K extends MessageKeys<NestedValueOf<Messages, NS>, NestedKeyOf<NestedValueOf<Messages, NS>>>>(
    key: K,
    values?: Record<string, unknown>,
  ): import('react').ReactNode
  has(key: NestedKeyOf<NestedValueOf<Messages, NS>>): boolean
  raw(key: NestedKeyOf<NestedValueOf<Messages, NS>>): unknown
}

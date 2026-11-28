import type { I18nTranslations, PartialTranslations } from '../types'

type AnyObject = { [key: string]: unknown }

/**
 * Deep merge two objects
 */
function deepMerge(target: AnyObject, source: AnyObject): AnyObject {
  const result = { ...target }

  for (const key in source) {
    if (Object.prototype.hasOwnProperty.call(source, key)) {
      const sourceValue = source[key]
      const targetValue = result[key]

      if (
        sourceValue !== null &&
        typeof sourceValue === 'object' &&
        !Array.isArray(sourceValue) &&
        targetValue !== null &&
        typeof targetValue === 'object' &&
        !Array.isArray(targetValue)
      ) {
        // Recursively merge objects
        result[key] = deepMerge(
          targetValue as AnyObject,
          sourceValue as AnyObject
        )
      } else if (sourceValue !== undefined) {
        // Override with source value
        result[key] = sourceValue
      }
    }
  }

  return result
}

/**
 * Merge base translations with partial overrides or additional namespaces
 *
 * @example
 * // Override existing keys
 * const customRu = mergeTranslations(ru, {
 *   ui: {
 *     select: {
 *       placeholder: 'Выберите марку авто...'
 *     }
 *   }
 * })
 *
 * @example
 * // Add app-specific namespace
 * const appTranslations = mergeTranslations(en, {
 *   hub: {
 *     nav: { home: 'Home' }
 *   }
 * })
 */
export function mergeTranslations<T extends Record<string, unknown> = Record<string, unknown>>(
  base: I18nTranslations,
  overrides: PartialTranslations | T
): I18nTranslations & T {
  return deepMerge(
    base as unknown as AnyObject,
    overrides as unknown as AnyObject
  ) as unknown as I18nTranslations & T
}

/**
 * Create translations from multiple partial sources
 *
 * @example
 * const translations = createTranslations(
 *   en,           // base
 *   uiOverrides,  // UI customizations
 *   appStrings    // App-specific strings
 * )
 */
export function createTranslations(
  base: I18nTranslations,
  ...overrides: PartialTranslations[]
): I18nTranslations {
  return overrides.reduce<I18nTranslations>(
    (acc, override) => mergeTranslations(acc, override),
    base
  )
}

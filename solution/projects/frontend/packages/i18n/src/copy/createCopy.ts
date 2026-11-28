import { useMemo } from 'react'

import { useLocaleOptional } from '../context'
import { resolveLocale, type Dictionaries, type Locale } from './locales'

export interface CopyKit<T> {
  /** Every bundled dictionary, for tests and tooling. */
  readonly dictionaries: Dictionaries<T>
  /** The dictionary for a language tag; English when it is not bundled. */
  resolve(tag: string | null | undefined): T
  /**
   * The dictionary for the active language: the `locale` prop when the host
   * passes one, else the `@djangocfg/i18n` provider, else English. With no
   * provider (a story, a test) it renders without one.
   */
  useCopy(locale?: string): T
  /** The bundled locale `useCopy` resolved to; feed it to `plural()`. */
  useLocale(locale?: string): Locale
}

/**
 * Wire a package's own dictionaries to the shared locale contract.
 *
 * The package keeps its strings and its `XCopy` schema; this supplies the one
 * resolver and the one hook, so locale handling is identical everywhere.
 */
export function createCopy<T>(dictionaries: Dictionaries<T>): CopyKit<T> {
  const resolve = (tag: string | null | undefined): T => dictionaries[resolveLocale(tag)]

  function useLocale(locale?: string): Locale {
    const fromProvider = useLocaleOptional()
    return resolveLocale(locale ?? fromProvider)
  }

  function useCopy(locale?: string): T {
    const resolved = useLocale(locale)
    return useMemo(() => dictionaries[resolved], [resolved])
  }

  return { dictionaries, resolve, useCopy, useLocale }
}

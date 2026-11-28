/**
 * The locales a self-contained package ships a dictionary for.
 *
 * One list for every widget: a package that forgets a language fails `tsc`
 * (see `Dictionaries`) instead of quietly rendering English for it.
 */
export const LOCALES = [
  'en', 'ru', 'ko', 'ja', 'de', 'fr', 'zh', 'it', 'es',
  'nl', 'ar', 'tr', 'pl', 'sv', 'no', 'da', 'pt-BR',
] as const

export type Locale = (typeof LOCALES)[number]

/**
 * A complete set of dictionaries. `Record` over the closed `Locale` union, so
 * a missing language is a type error at the registry, not a runtime miss.
 */
export type Dictionaries<T> = Readonly<Record<Locale, T>>

/** Language tags hosts report that name one of our locales under another code. */
const ALIASES: Readonly<Record<string, Locale>> = {
  nb: 'no',
  nn: 'no',
  pt: 'pt-BR',
  'pt-pt': 'pt-BR',
}

const BY_LOWER = new Map<string, Locale>(LOCALES.map((l) => [l.toLowerCase(), l]))

/**
 * Map whatever language tag the host reports to a bundled locale.
 *
 * Exact match, then the base language (`zh-CN` → `zh`), then an alias
 * (`nb` → `no`), then English. One resolver for every package, so two widgets
 * on one page never disagree about what `pt` means.
 */
export function resolveLocale(tag: string | null | undefined): Locale {
  if (!tag) return 'en'
  const lower = tag.replace('_', '-').toLowerCase()
  const exact = BY_LOWER.get(lower)
  if (exact) return exact
  const alias = ALIASES[lower]
  if (alias) return alias
  const base = lower.split('-')[0] ?? ''
  return BY_LOWER.get(base) ?? ALIASES[base] ?? 'en'
}

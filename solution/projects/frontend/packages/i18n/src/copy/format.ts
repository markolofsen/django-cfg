/** The plural categories `Intl.PluralRules` can report; only `other` is required. */
export interface PluralCopy {
  readonly zero?: string
  readonly one?: string
  readonly two?: string
  readonly few?: string
  readonly many?: string
  readonly other: string
}

export type FillValues = Readonly<Record<string, string | number>>

/**
 * Fill `{{name}}` placeholders. The placeholder belongs to the dictionary, so a
 * translator can move it; a template literal at the call site could not.
 */
export function fill(template: string, values: FillValues): string {
  return template.replace(/\{\{(\w+)\}\}/g, (whole, key: string) => {
    const value = values[key]
    return value === undefined ? whole : String(value)
  })
}

// Building a PluralRules costs a locale-data lookup and plurals render often.
const rules = new Map<string, Intl.PluralRules>()

function rulesFor(language: string): Intl.PluralRules {
  const cached = rules.get(language)
  if (cached) return cached
  let made: Intl.PluralRules
  try {
    made = new Intl.PluralRules(language)
  } catch {
    // An invalid tag throws; a wrong plural beats a crashed render.
    made = new Intl.PluralRules('en')
  }
  rules.set(language, made)
  return made
}

/** Pick the plural form for `count` and fill `{{count}}`; `other` is the fallback. */
export function plural(
  copy: PluralCopy,
  count: number,
  language: string,
  values: FillValues = {},
): string {
  const template = copy[rulesFor(language).select(count)] ?? copy.other
  return fill(template, { ...values, count })
}

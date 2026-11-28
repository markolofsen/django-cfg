import { readdirSync } from 'node:fs'

import { LOCALES } from './locales'

type Tree = { readonly [key: string]: string | Tree }

function leaves(tree: Tree, prefix = ''): Map<string, string> {
  const out = new Map<string, string>()
  for (const [key, value] of Object.entries(tree)) {
    const path = prefix ? `${prefix}.${key}` : key
    if (typeof value === 'string') out.set(path, value)
    else for (const [p, v] of leaves(value, path)) out.set(p, v)
  }
  return out
}

const placeholders = (s: string): string =>
  [...s.matchAll(/\{{1,2}(\w+)\}{1,2}/g)].map((m) => m[1]).sort().join(',')

// A language has the plural forms it has (`ko` has no `one`, `ru` adds `few`
// and `many`), so only `other` is a fixed key under a `PluralCopy`.
const OPTIONAL_FORMS = new Set(['zero', 'one', 'two', 'few', 'many'])
const isOptionalForm = (path: string): boolean => OPTIONAL_FORMS.has(path.split('.').pop() ?? '')

const norm = (s: string): string => s.replace('-', '').toLowerCase()

/**
 * What `tsc` cannot check about a package's dictionaries; returns problems,
 * empty when clean:
 *
 * - the registry covers every locale in `LOCALES`;
 * - every file in `localesDir` is registered (written, never wired in);
 * - every dictionary has the same keys as English (plural forms other than
 *   `other` may differ per language);
 * - every string is non-blank and keeps the `{{placeholders}}` English has.
 *
 * `dictionaries` is typed loosely so any `XCopy` can be passed without a cast.
 */
export function checkDictionaries(
  dictionaries: Readonly<Record<string, object>>,
  localesDir: string,
): string[] {
  const problems: string[] = []
  const registered = Object.keys(dictionaries)

  for (const locale of LOCALES) {
    if (!registered.includes(locale)) problems.push(`locale not registered: ${locale}`)
  }

  const onDisk = readdirSync(localesDir)
    .filter((n) => n.endsWith('.ts'))
    .map((n) => n.replace(/\.ts$/, ''))
  if (onDisk.length === 0) problems.push(`no dictionary files in ${localesDir}`)
  for (const file of onDisk) {
    if (!registered.some((k) => norm(k) === norm(file))) {
      problems.push(`file not registered: ${file}`)
    }
  }

  const en = dictionaries.en
  if (!en) return [...problems, 'no English dictionary']
  const reference = leaves(en as Tree)
  for (const [locale, dict] of Object.entries(dictionaries)) {
    const own = leaves(dict as Tree)
    for (const [path, text] of reference) {
      const got = own.get(path)
      if (got === undefined) {
        if (!isOptionalForm(path)) problems.push(`${locale}: missing ${path}`)
      } else if (got.trim() === '') problems.push(`${locale}: blank ${path}`)
      else if (placeholders(got) !== placeholders(text)) {
        problems.push(`${locale}: placeholders differ at ${path}`)
      }
    }
    for (const path of own.keys()) {
      if (!reference.has(path) && !isOptionalForm(path)) problems.push(`${locale}: extra ${path}`)
    }
  }
  return problems
}

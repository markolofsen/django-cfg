<div align="center">

![@djangocfg/i18n](https://raw.githubusercontent.com/markolofsen/assets/main/libs/djangocfg/i18n.webp)

</div>

# @djangocfg/i18n

Lightweight, type-safe i18n library for @djangocfg packages.

## Features

- **17 languages** — en, ru, ko, ja, de, fr, zh, it, es, nl, ar, tr, pt-BR, pl, sv, no, da
- **Type-safe** — Full TypeScript support with autocomplete
- **CLI included** — Manage locales from the terminal
- **Works standalone** — Components work without provider

## Installation

```bash
pnpm add @djangocfg/i18n
```

## Quick Start

```tsx
import { I18nProvider, useT, ru } from '@djangocfg/i18n'

<I18nProvider locale="ru" translations={ru}>
  <App />
</I18nProvider>

function MyComponent() {
  const t = useT()
  return <span>{t('ui.form.save')}</span>
}
```

## Subpath Imports (Server Components)

```tsx
// ✅ Server-safe (no React Context)
import { en, ru, ko } from '@djangocfg/i18n/locales'
import { mergeTranslations } from '@djangocfg/i18n/utils'

// ❌ Client-only (has React Context)
import { I18nProvider, useT } from '@djangocfg/i18n'
```

| Path | Description |
|------|-------------|
| `@djangocfg/i18n` | Full package (client components) |
| `@djangocfg/i18n/locales` | Locale data only (server-safe) |
| `@djangocfg/i18n/utils` | Utilities like `mergeTranslations` (server-safe) |

## Self-contained copy

Widgets ship their own typed dictionaries and share one locale contract:

```ts
import { createCopy, type Locale } from '@djangocfg/i18n/copy'

const DICTIONARIES: Record<Locale, MyCopy> = { en, ru, /* ... */ 'pt-BR': ptBR }
export const useMyCopy = createCopy(DICTIONARIES).useCopy
```

See [`@docs/SELF_CONTAINED_COPY.md`](./@docs/SELF_CONTAINED_COPY.md).

## CLI

```bash
# Check missing keys across locales
pnpm i18n check

# List / search keys
pnpm i18n list
pnpm i18n list tour        # filter by pattern
pnpm i18n list -v          # with values

# Add key to all locales at once
pnpm i18n add "tools.new" '{"en":"New","ru":"Новый"}'

# Work with app locales in another directory
pnpm i18n check -d ../../apps/hub/i18n/locales
pnpm i18n list -d ../../apps/hub/i18n/locales
```

## Hooks

| Hook | Description |
|------|-------------|
| `useT()` | Returns translation function (recommended) |
| `useI18n()` | Full context: `{ t, locale, setLocale, translations }` |
| `useLocale()` | Returns current locale string |
| `useTypedT<T>()` | Type-safe with compile-time key validation |

### useT()

```tsx
function MyComponent() {
  const t = useT()
  return <button>{t('ui.form.save')}</button>
}
```

### useI18n()

```tsx
function LocaleSwitcher() {
  const { t, locale, setLocale } = useI18n()

  return (
    <select value={locale} onChange={(e) => setLocale(e.target.value)}>
      <option value="en">English</option>
      <option value="ru">Russian</option>
    </select>
  )
}
```

## Type-safe next-intl Integration

Override `useTranslations` in your app's `global.d.ts` to get compile-time key validation.

```ts
// global.d.ts
type _Messages = import('@djangocfg/i18n').I18nTranslations &
  import('./i18n/locales/types').AppTranslations;

type _NSKeys = import('@djangocfg/i18n').NamespaceKeys<
  _Messages,
  import('@djangocfg/i18n').NestedKeyOf<_Messages>
>;

declare module 'next-intl' {
  export function useTranslations<NS extends _NSKeys>(
    namespace: NS,
  ): import('@djangocfg/i18n').IntlTranslator<_Messages, NS>;
}
```

## Extending Translations

```ts
// Spread merge (recommended for next-intl)
import { en as baseEn } from '@djangocfg/i18n/locales'
const messages = { ...baseEn, ...appEn }

// Deep merge with overrides
import { mergeTranslations, ru } from '@djangocfg/i18n'
const customRu = mergeTranslations(ru, {
  ui: { select: { placeholder: 'Выберите...' } },
})
```

## Interpolation

```tsx
t('ui.pagination.showing', { from: 1, to: 10, total: 100 })
// => "1-10 of 100"
```

## Translation Key Paths

```
ui.*         - UI components (select, form, dialog, table, pagination)
layouts.*    - Layout components (sidebar, auth, profile, theme)
api.*        - API/network messages
tools.*      - Heavy tools (tour, upload, code, image)
```

## Works Without Provider

Components using `useT()` fall back to English defaults when used outside a provider.

## License

MIT

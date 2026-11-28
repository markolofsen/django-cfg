# @djangocfg/nextjs/og-image

Page metadata for Next.js: title templating, canonical + hreflang alternates,
OpenGraph, Twitter cards and icons, from one bound factory.

> **Changed 2026-09-03.** This package used to build URLs for a Django-side PNG
> renderer (`django_ogimage`, `/cfg/og/<base64>/`). That module is archived and
> the `'dynamic'` / `{ render }` specs, `ogBackend`, `buildOgUrl`,
> `createOgMetadata`, `withOgImage` and `OGImageParams` are gone with it.
> Next.js renders per-page cards itself — see [Per-page cards](#per-page-cards).

---

## Quick start

One factory per app; pages declare only what's unique.

```typescript
// app/_core/metadata.ts — bind the factory once
import { makeMetadataFactory } from '@djangocfg/nextjs/og-image'
import { settings } from './settings'
import { LOCALES } from '@i18n/locales.config'

export const createMetadata = makeMetadataFactory({
  name: settings.app.name,
  description: settings.app.description,
  siteUrl: settings.app.siteUrl,
  ogImage: settings.app.media.ogimage,     // static brand card (the default)
  icons: { icon: settings.app.media.favicon },
  locales: LOCALES,                        // omit for single-locale sites
})

// any page.tsx
export const metadata = createMetadata({ title: 'Pricing', path: '/pricing' })
//                        ↑ brand image, canonical, hreflang, og, twitter, icons
```

```typescript
// content page with its own image (a screenshot, cover, …)
export const metadata = createMetadata({ title: p.name, path, og: { image: p.image, alt: p.name } })
```

### The `og` axis (`OgSpec`)

| `og` value | Result |
|---|---|
| omitted / `'static'` | the brand image from `config.ogImage` (default) |
| `{ image, alt? }` | that exact URL |

Both cases resolve in `resolveOgImage` — the one place that decides what the OG
image is. `og:image` and `twitter:image` are always written together there,
because a change that set one and not the other is the failure this package
exists to prevent.

---

## Per-page cards

To render a card per page — the title on a background, a generated cover —
use Next.js's own file convention:

```tsx
// app/blog/[slug]/opengraph-image.tsx
import { ImageResponse } from 'next/og'

export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'

export default async function Image({ params }) {
  return new ImageResponse(<div style={{ /* … */ }}>{title}</div>, size)
}
```

**The route alone is not enough.** Next.js applies the file convention only
when a page's metadata leaves `openGraph.images` unset — an explicit value
wins, and the route is then silently never rendered. `createMetadata` always
writes `openGraph.images` (both `OgSpec` cases resolve to an image), so adding
`opengraph-image.tsx` under a page built by this factory does nothing.

To actually get the card, strip the key the factory set:

```tsx
// app/blog/[slug]/page.tsx
const { openGraph, twitter, ...rest } = createMetadata({ title: p.name, path })
const { images: _og, ...og } = openGraph ?? {}
const { images: _tw, ...tw } = twitter ?? {}
export const metadata = { ...rest, openGraph: og, twitter: tw }
```

The factory has no "dynamic" case because the card is Next.js's job to render,
not this package's — but the two mechanisms do compete for the same tag, and
the explicit one wins.

---

## API

#### `makeMetadataFactory(config) → (page) => Metadata`

Binds a `SiteMetaConfig` once and returns a per-page factory. The recommended
entry point.

**`SiteMetaConfig`**

| Field | Type | Notes |
|---|---|---|
| `name` | `string` | brand name (titles, siteName, alt) |
| `description` | `string` | default description |
| `siteUrl` | `string` | absolute origin, e.g. `https://example.com` |
| `ogImage` | `string` | static brand OG image URL |
| `icons?` | `Metadata['icons']` | favicon / apple-touch |
| `locales?` | `readonly string[]` | for hreflang; omit for single-locale |
| `defaultLocale?` | `string` | x-default locale (defaults `en` / first) |

**`PageMeta`**

| Field | Type | Notes |
|---|---|---|
| `title?` | `string` | falls back to `config.name` |
| `description?` | `string` | falls back to `config.description` |
| `keywords?` | `string[]` | |
| `locale?` | `string` | canonical + `openGraph.locale` |
| `path?` | `string` | path without locale prefix, `''` for home |
| `og?` | `OgSpec` | the OG image axis (see table above) |
| `extra?` | `Metadata` | escape hatch merged last (robots, authors, title-template, …) |

#### `createMetadata(config, page)`

The un-curried form `makeMetadataFactory` wraps. Use when you don't want a bound
factory.

#### `resolveOgImage(spec, staticUrl, fallbackTitle)` · `extractTitle(metadata)`

Escape hatches for custom factories. Most pages never touch them.

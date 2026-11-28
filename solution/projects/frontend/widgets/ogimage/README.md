# @djangocfg/widget-ogimage

Open Graph cards for Next.js apps. What a link **becomes** when someone pastes
it into WhatsApp, Telegram, Slack, iMessage or Facebook — often the only part
of a site a person sees before deciding whether to open the page.

One satori renderer, the vendored Plus Jakarta Sans, and the two card
"fabrics" every `opengraph-image.tsx` calls. Brand identity is bound once per
app, so two apps on this package draw from the same layout and still read as
two products.

## Quick start

```tsx
// app/_lib/og.tsx — bind the identity once
import { createOgCards, domainFromEnv } from '@djangocfg/widget-ogimage';
import { settings } from '@core/settings';

export const { size, contentType, brandCard, contentCard } = createOgCards({
  name: settings.app.name,
  description: settings.app.description,
  tagline: 'Run on one machine. Coordinate many.',
  domain: domainFromEnv({ fallback: settings.app.siteUrl }),
  siteUrl: settings.app.siteUrl,
  accentColor: '#61B8FF',
  mark: <svg …/>, // inline SVG only — see below
});
```

```tsx
// app/opengraph-image.tsx — the brand card: home, and the fallback everywhere
import { brandCard, contentType, size } from '@lib/og';

export const runtime = 'nodejs';
export const alt = 'CMDOP — run commands across your machines';
export { size, contentType };

export default async function OpengraphImage() {
  return brandCard('Skills & MCP servers', 'Browse, search, and install.');
}
```

```tsx
// app/skills/[slug]/opengraph-image.tsx — one entity
import { contentCard, contentType, size } from '@lib/og';
import { getSkill } from '@lib/api';

export const runtime = 'nodejs';
export { size, contentType };

export default async function Image({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const skill = await getSkill(slug).catch(() => null); // never throw — see rules

  return contentCard({
    title: skill?.seoTitle || skill?.name, // empty → brand card
    eyebrow: 'Skill',
    description: skill?.seoDescription,
    footer: 'Marketplace · Skills',
    image: skill?.cover, // absolute URL, root-relative path, or data URI
  });
}
```

Check locally by appending the segment to any page path:
`/opengraph-image`, `/skills/<slug>/opengraph-image`. Both return a 1200×630 PNG.

## Three rules

**`runtime = 'nodejs'` on every route.** The font decoder uses `Buffer`, which
the edge runtime does not provide.

**Never throw.** A card renders while a crawler waits. A route that 500s leaves
a bare grey rectangle in the chat thread — strictly worse than a generic brand
card. Every fetch is `.catch(() => null)`, and `contentCard` falls back to
`brandCard` when the title is empty.

**No `openGraph.images` above a card.** Next's file convention only applies
where no explicit `images` is set in metadata, and an explicit entry *wins*.
An `images` array in a layout does not complement the cards below it, it
silently disables them — the root layout can suppress every card in the app at
once. `withoutOgImages(metadata)` strips them from generated metadata.

## API

| Export | Role |
|---|---|
| `createOgCards(config)` | Binds identity → `{ size, contentType, brandCard, contentCard }`. The recommended entry point. |
| `fitDescription(title, text)` | Description budget as a function of title length; trims at a word boundary. |
| `ogFooter(...parts)` | Joins facts with ` · `, dropping absent ones. |
| `ogImageUrl(path, siteUrl)` | Absolute URL or `undefined` — satori fetches images itself. |
| `domainFromEnv` · `siteUrlFromEnv` · `metadataBaseFromEnv` · `resolvePublicUrl` | Site origin from `NEXT_PUBLIC_SITE_URL` with an app-owned fallback. |
| `withoutOgImages(metadata)` | Strips `openGraph.images` / `twitter.images` so a segment's card applies. |
| `renderOgImage(options, fonts)` · `OG_SIZE` · `OG_CONTENT_TYPE` · `DEFAULT_OG_THEME` | Draw a card directly. |
| `loadOgFonts()` | The vendored typeface, decoded once per process. |
| `loadImageDataUri(path, mime)` | A local file as a data URI (a portrait that ships with the app). |

### `OgCardsConfig`

| Field | Notes |
|---|---|
| `name` | brand card title; wordmark on content cards |
| `description?` · `tagline?` | brand card description and footer |
| `domain?` | printed bottom-right |
| `siteUrl?` | resolves root-relative `image` paths |
| `accentColor?` · `theme?` | palette; `theme.footer` defaults to the accent |
| `mark?` | inline SVG. Satori cannot load React icon components with CSS, and an `<img>` to a remote logo makes every card depend on a fetch that can fail while a crawler waits. |
| `loadFonts?` | swap the typeface |

## Layout

The frame is 1200×630 and satori does not clip: a title long enough to wrap
pushes into the footer instead of truncating. `titleSizeFor` steps the title
through 84 → 66 → 52px at 34 and 58 characters, and `fitDescription` budgets
the description against those same steps (150 → 92 → 0 characters), so the two
move together. Change one, change the other.

Over a photograph a two-pass scrim darkens the left half so the copy survives
whatever the image happens to be, and the copy column narrows to stay on the
scrimmed ground. The numbers were arrived at by rendering; if you change them,
render one and look at it.

## Fonts

`src/fonts/index.ts` is **generated** — the three `.woff` files beside it are
the source of truth. Satori cannot use `next/font` (woff2, returns class
names) and cannot read a `.woff` beside a route in a production build (nothing
traces it into the output), so the bytes are inlined as base64 into the module
graph. ~64KB of source, paid at build time, never sent to a browser.

```bash
pnpm fonts   # node scripts/generate-fonts.mjs
```

Plus Jakarta Sans, SIL Open Font License 1.1. The original font copyright
and full license are included in [src/fonts/OFL.txt](src/fonts/OFL.txt),
including for the generated inlined font bytes.

## Metadata

Page `Metadata` (title template, canonical, hreflang, static brand image) is
`@djangocfg/nextjs/og-image`'s `makeMetadataFactory`. It has no "render a
card" case on purpose: the file convention above overrides metadata by design,
so supporting both would be two mechanisms competing to set the same tag.

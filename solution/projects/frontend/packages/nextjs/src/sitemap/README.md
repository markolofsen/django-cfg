# @djangocfg/nextjs/sitemap

Frontend half of the djangocfg ↔ Next.js sitemap integration.

The Django-side backend (`django_cfg.modules.django_sitemap`) exposes a
paginated JSON feed. This subpackage turns that feed into a Google-compliant
XML sitemap-index via Next.js's native `generateSitemaps()` API.

## Why this exists

Two naive approaches fail at scale:

1. **Django serves XML directly** — wrong host (api.example.com vs
   www.example.com), can't include frontend-only routes, hard to add
   per-locale alternates, awkward sitemap-index dance.
2. **Frontend queries the DB** — frontends don't have DB access; falling
   back to public REST endpoints means N round trips and no streaming.

This package solves both. Django returns path-only JSON; the frontend
joins the host and emits sitemap-index XML. Same backend can serve
multiple frontends (preview, staging, EU domain) — they each bring their
own host.

## The big picture

```
┌──────────────────────────────────────────────────────────────────────┐
│ Django app (e.g. apps/catalog)                                       │
│   sitemap_sources.py                                                 │
│     register(SitemapSource(                                          │
│       name="vehicles",                                               │
│       queryset_factory=lambda: Vehicle.objects.sitemap_eligible(),   │
│       url_template="/catalog/{id}",                                  │
│       lastmod_field="last_seen_at",                                  │
│       cursor_fields=("last_seen_at", "id"),                          │
│       order="-last_seen_at,-id",                                     │
│       page_size=50_000,                                              │
│     ))                                                               │
└──────────────────────────┬───────────────────────────────────────────┘
                           │ AppConfig.ready() → in-process registry
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│ django_cfg.modules.django_sitemap (HTTP layer)                       │
│                                                                      │
│   GET /cfg/sitemap/index/                                            │
│     → list of chunks per source, with opaque keyset cursors          │
│                                                                      │
│   GET /cfg/sitemap/feed/?source=<name>&cursor=<opaque>               │
│     → 50 000 entries: { loc, lastmod }                               │
│                                                                      │
│   Cache-Control: public, s-maxage=3600, stale-while-revalidate=86400 │
└──────────────────────────┬───────────────────────────────────────────┘
                           │ HTTP (server-side fetch from Next)
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Next.js app — apps/<app>/app/                                        │
│                                                                      │
│   sitemap.ts                                                         │
│     createDjangoSitemap({ host, apiUrl, staticRoutes })              │
│     ├ generateSitemaps()  — reads /cfg/sitemap/index/, returns ids   │
│     └ default sitemap()   — fetches one /cfg/sitemap/feed/ per id    │
│                                                                      │
│   robots.ts                                                          │
│     createRobots({ host, disallow })                                 │
└──────────────────────────────────────────────────────────────────────┘
```

Next emits:

- `/sitemap.xml` — auto-generated `<sitemapindex>` listing every chunk.
- `/sitemap/<id>.xml` — one `<urlset>` per chunk (50k URLs max, per
  Google's cap).
- `/robots.txt` — points crawlers at `/sitemap.xml`.

## Quick start

### 1. Register sources in Django

```python
# apps/<your-app>/sitemap_sources.py
from django_cfg.modules.django_sitemap import SitemapSource, register
from apps.catalog.models import Vehicle, Brand

register(SitemapSource(
    name="vehicles",
    url_template="/catalog/{id}",
    queryset_factory=lambda: Vehicle.objects.get_queryset().sitemap_eligible(),
    fields={"id": "id"},
    lastmod_field="last_seen_at",
    cursor_fields=("last_seen_at", "id"),
    order="-last_seen_at,-id",
    page_size=50_000,
))

register(SitemapSource(
    name="brands",
    url_template="/catalog?brand={slug}",
    queryset_factory=lambda: Brand.objects.filter(is_active=True),
    fields={"slug": "slug"},
    lastmod_field="updated_at",
    cursor_fields=("slug",),
    order="slug",
))
```

`SitemapAppConfig.ready()` autoloads every installed app's
`sitemap_sources.py` — no host-side wiring needed. Verify with
`python manage.py sitemap_inspect`.

### 2. Wire up the frontend

```tsx
// apps/<your-app>/app/sitemap.ts
import { createDjangoSitemap } from '@djangocfg/nextjs/sitemap';

const { generateSitemaps, sitemap } = createDjangoSitemap({
  host: process.env.NEXT_PUBLIC_SITE_URL!,
  apiUrl: process.env.NEXT_PUBLIC_API_URL!,
  staticRoutes: [
    { path: '/', changeFrequency: 'daily', priority: 1.0 },
    { path: '/catalog', changeFrequency: 'daily', priority: 0.9 },
    { path: '/ai-search', changeFrequency: 'weekly', priority: 0.7 },
  ],
});

export { generateSitemaps, sitemap as default };
export const revalidate = 3600;
```

```tsx
// apps/<your-app>/app/robots.ts
import { createRobots } from '@djangocfg/nextjs/sitemap';

export default createRobots({
  host: process.env.NEXT_PUBLIC_SITE_URL!,
  disallow: ['/account/', '/auth', '/api/', '/apix/'],
});
```

That's the whole app-side integration.

## Backend without backend

Marketing sites and documentation portals usually don't have a Django
catalog to paginate. Omit `apiUrl` — the frontend then emits a
single-chunk sitemap from `staticRoutes` only.

```tsx
const { generateSitemaps, sitemap } = createDjangoSitemap({
  host: 'https://example.com',
  staticRoutes: [
    { path: '/', priority: 1.0 },
    { path: '/about', priority: 0.8 },
    { path: '/pricing', priority: 0.9 },
  ],
});
```

## What gets emitted

For a 1 200 000-vehicle catalog + 6 static pages:

- `/sitemap.xml` — index with ~25 child entries (24 vehicle chunks +
  brands + models + static).
- `/sitemap/static.xml` — 6 static URLs with `<changefreq>`/`<priority>`.
- `/sitemap/vehicles--<cursor>.xml` × 24 — 50 000 vehicle URLs each
  (sorted by `last_seen_at DESC` so the freshest listings live in chunk 1
  and Googlebot re-crawls them first).
- `/sitemap/brands--.xml` — one chunk.
- `/sitemap/models--.xml` — one chunk.

**Only `loc` and `lastmod`** are emitted from backend entries: Google
ignores `<changefreq>` and `<priority>` on dynamic URLs, and omitting
them keeps the payload small. Static routes still emit them — non-Google
crawlers (Bing, Yandex) read those fields, and they're free.

## Cache layers

Three layers cooperate; each TTL aligned with how often the data
*actually* changes.

| Layer | Default TTL | Tuned via |
|---|---|---|
| Django Redis (sitemap-index JSON) | 5 min | `SitemapConfig.cache_index_seconds` |
| Django Redis (per-chunk JSON) | 1 h | `SitemapConfig.cache_feed_seconds` |
| Next.js ISR (XML) | 1 h | `createDjangoSitemap({ feedRevalidate })` + `export const revalidate = ...` |
| HTTP `Cache-Control` | `s-maxage=3600, swr=86400` | Django sets, CDN respects |

Result: Googlebot fetching `/sitemap.xml` rarely touches Django — most
hits land on the CDN edge or Next ISR. Django only does real work once
per TTL.

To force a cache bust without `FLUSHDB`, bump `SitemapConfig.cache_version`
on the Django side; every Redis key includes it.

## Failure mode

`fetchSitemapIndex` and `fetchSitemapFeed` behave differently in the two
phases.

**During `next build`** (`NEXT_PHASE=phase-production-build`) they never
throw. A Django outage is downgraded:

- empty index → only the static chunk is emitted
- empty feed → that chunk renders an empty `<urlset/>`

The build completes with no coupling to Django uptime, and the next ISR cycle
heals it.

**At runtime they throw.** On a failed regeneration Next keeps serving the
last good copy. The old runtime fallback cached the degraded answer for the
whole revalidate window: a Traefik 404 during a Django recreate became a
static-only sitemap index for ten minutes. A consumer that diffs the sitemap,
such as an IndexNow sweep, then read every listing as removed and resubmitted
the entire catalogue. A cold start with Django down answers 500 until Django
is back, which a crawler retries.

## Deployment

### Env vars

```
NEXT_PUBLIC_SITE_URL=https://example.com         # canonical host
NEXT_PUBLIC_API_URL=https://api.example.com      # Django backend
```

Both are public — sitemap.ts runs on the server but the same `host` is
also embedded in client-side metadata.

### Docker

Nothing sitemap-specific is required in the container — the package is a
plain TypeScript dependency, no native modules, no extra ports. Just pass
the two env vars above via `env_file` or `environment:`.

The Next service's existing healthcheck on `/` is enough; no separate
sitemap probe needed (a missing sitemap doesn't break the app).

### CDN / Cloudflare

Cache by URL, respect origin `Cache-Control`:

| URL pattern | TTL fresh | TTL stale |
|---|---|---|
| `/sitemap.xml` | 1 h | 1 day |
| `/sitemap/*.xml` | 1 h | 1 day |
| `/robots.txt` | 24 h | 1 day |

Stale-while-revalidate keeps Googlebot fast even during a Django outage.

### Sitemap submission

Submit `https://<host>/sitemap.xml` once via Google Search Console.
Google polls it on its own schedule afterwards — no `ping` integration
needed.

## API reference

### `createDjangoSitemap(options)`

Returns `{ generateSitemaps, sitemap }`. Export them as Next.js
expects: named `generateSitemaps` + default-exported `sitemap`.

**Options:**

| Field | Type | Default | Notes |
|---|---|---|---|
| `host` | `string` | (required) | Canonical host (e.g. `https://example.com`). URLs are joined as `${host}${loc}`. |
| `apiUrl` | `string` | `undefined` | Django backend base URL. Omit to skip the backend feed entirely. |
| `staticRoutes` | `StaticRoute[]` | `[]` | Frontend-only routes. Auth/account routes should NOT be listed here. |
| `sources` | `string[] \| (name) => boolean` | every source | Which backend sources this frontend claims. See [Several frontends, one backend](#several-frontends-one-backend). |
| `indexRevalidate` | `number` | `600` | Seconds — `next: { revalidate }` on the index fetch. |
| `feedRevalidate` | `number` | `3600` | Seconds — `next: { revalidate }` on each chunk fetch. |

**`StaticRoute`:**

```ts
interface StaticRoute {
  path: string;
  changeFrequency?: 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never';
  priority?: number;  // 0.0 – 1.0
}
```

### `createRobots(options)`

Returns a Next.js `() => MetadataRoute.Robots` function. Default-export
it from `app/robots.ts`.

**Options:**

| Field | Type | Default | Notes |
|---|---|---|---|
| `host` | `string` | (required) | Canonical host. |
| `disallow` | `string[]` | `['/account/', '/auth', '/api/']` | Path prefixes to block. |
| `sitemap` | `string` | `${host}/sitemap.xml` | Override the sitemap pointer. |

## Several frontends, one backend

`GET /cfg/sitemap/index/` answers for the whole Django project — every
source any installed app registered. When one backend serves several
brands, register a source per brand and give each frontend its own:

```python
# apps/catalog/sitemap_sources.py
for portal in ("caribbean", "bali"):
    register(SitemapSource(name=f"properties-{portal}", ...))
```

```ts
// apps/web-bali/app/sitemap.ts
import { createDjangoSitemap, tenantSources } from '@djangocfg/nextjs/sitemap';

const { generateSitemaps, sitemap } = createDjangoSitemap({
  host, apiUrl,
  sources: tenantSources('bali'),   // properties-bali, communities-bali, …
});
```

```ts
// apps/web-bali/app/sitemap_index.xml/route.ts — the SAME selector
export const { GET } = createSitemapIndex({
  host, apiUrl,
  sources: tenantSources('bali'),
});
```

Pass the same selector to both. The index lists chunks, `sitemap.ts`
builds them; a mismatch advertises shards that render empty, and nothing
fails loudly when it happens.

**Why the frontend filters and not the backend.** The index view is
cached under a key with no tenant dimension, so a `?tenant=` parameter
would pass every cold-cache test and then serve one brand's chunk list
to the other an hour later. Source names carry the distinction instead:
an unknown source 404s, which is a loud failure rather than a silent
wrong one.

`tenantSources` splits the source name on its LAST hyphen and compares
the tail exactly. Prefer it over `endsWith('-bali')`, which also matches
a `pricing-plans-premium` for a tenant named `premium`. Names without a
hyphen never match — an untenanted source belongs to the project, not to
a brand.

Omit `sources` entirely when the backend serves this frontend alone.

### Lower-level utilities

Exposed for advanced use cases (custom Next route handlers, debugging):

```ts
import {
  fetchSitemapIndex,
  fetchSitemapFeed,
  encodeChunkId,
  decodeChunkId,
  selectSources,
  sourceFilter,
  tenantSources,
} from '@djangocfg/nextjs/sitemap';
```

## When NOT to use this

- Sites under ~1 000 URLs with no backend pagination needs — a flat
  `staticRoutes`-only configuration is fine, but a hand-written
  `sitemap.ts` returning a literal array works just as well.
- You need per-locale `<xhtml:link rel="alternate">` tags — not currently
  emitted; the wire contract has room for it (`alternates`) but no
  consumer requires it yet.
- You need image/video/news sitemap extensions — not implemented.

## See also

- `django_cfg.modules.django_sitemap` — backend module (registry, HTTP
  views, `sitemap_inspect` management command).
- [Next.js docs — generateSitemaps](https://nextjs.org/docs/app/api-reference/functions/generate-sitemaps)
- [Google — large sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/large-sitemaps)

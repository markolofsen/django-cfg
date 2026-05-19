# django_sitemap

Reusable sitemap source registry + paginated JSON feed for djangocfg-based
projects. Designed to feed a Next.js (or any other) frontend that turns the
JSON into search-engine-ready XML.

Built for catalogs at scale — keyset pagination, Redis caching, and a
quality filter built into the source queryset rather than the sitemap
generator. Tested on a 2M-row vehicle catalog.

## Why this module exists

Two naive approaches fail at scale:

1. **Django serves XML directly** via `django.contrib.sitemaps`. Wrong host
   (api.example.com vs www.example.com), can't include frontend-only
   routes, hard to add per-locale alternates, and the 50k-URL-per-file
   sitemap-index dance is awkward.
2. **Frontend queries the DB**. Frontends don't have DB access; falling
   back to public REST endpoints means N round trips and no streaming.

`django_sitemap` solves both: Django exposes a typed JSON contract,
frontend consumes it and emits XML. Path-only URLs (no host baked in)
mean one backend can serve multiple frontends.

## What ships

```
django_sitemap/
  __init__.py                     # public: register, SitemapSource, get_sitemap_config
  apps.py                         # autoload <app>.sitemap_sources on AppConfig.ready()
  config.py                       # SitemapConfig (Pydantic) — cache TTLs, page size
  registry.py                     # process-wide source registry
  sources.py                      # SitemapSource model + resolve_field helper
  cursors.py                      # opaque base64-JSON cursors for keyset pagination
  pagination.py                   # keyset_page() — constant-time per chunk
  cache.py                        # Redis wrappers with versioned keys
  http/
    views.py                      # SitemapIndexView + SitemapFeedView (plain Django)
    urls.py                       # /cfg/sitemap/{index,feed}/
  management/commands/
    sitemap_inspect.py            # CLI — list sources + counts + sample URLs
```

## Wire-up

The module ships as a Django app and is auto-registered into djangocfg's
default `INSTALLED_APPS` plus the `cfg/sitemap/` URL include. No host-side
config required.

## Quick start

In your Django app, create `sitemap_sources.py` next to `models.py`:

```python
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
`sitemap_sources.py` — the file's import side effect is the registration.

Verify with the management command:

```
$ python manage.py sitemap_inspect

Source    Total   Chunks  Sample URL
--------  ------  ------  ---------------------------------------------
vehicles  26201   1       /catalog/dd9951e4-0a03-45a3-b49c-…
brands    102     1       /catalog?brand=abarth
```

## HTTP contract

### `GET /cfg/sitemap/index/`

Chunk catalog across every registered source. Cached in Redis for
`SitemapConfig.cache_index_seconds` (default 300).

```jsonc
{
  "sources": [
    {
      "name": "vehicles",
      "chunks": [
        { "id": "vehicles-1", "cursor_to": "MjAyNi0w…", "count_estimate": 50000 },
        { "id": "vehicles-2", "cursor_to": null,        "count_estimate": 17821 }
      ],
      "total_estimate": 67821
    }
  ],
  "generated_at": "2026-05-17T10:00:00+00:00",
  "ttl_seconds": 300
}
```

### `GET /cfg/sitemap/feed/?source=<name>&cursor=<opaque>`

One chunk of entries. Cached in Redis for `cache_feed_seconds` (default
3600).

```jsonc
{
  "source": "vehicles",
  "chunk_id": "vehicles-1",
  "count": 50000,
  "has_more": true,
  "next_cursor": "MjAyNi0w…",
  "entries": [
    { "loc": "/catalog/abc-123", "lastmod": "2026-05-17T09:00:00+00:00" }
  ]
}
```

Notes:

- `loc` is a **path**, not a URL — the frontend joins the host. This is
  what lets one backend serve multiple frontends.
- Only `loc` + `lastmod` are emitted. Google ignores `<changefreq>` and
  `<priority>`; we save bytes by not generating them.
- Errors: missing `source` → 400, unknown source → 404, malformed cursor
  → 400.

Both endpoints emit
`Cache-Control: public, s-maxage=<ttl>, stale-while-revalidate=<ttl*24>`
so a CDN in front (Cloudflare) can serve stale during origin hiccups.

## SitemapSource fields

| Field | Required | Notes |
|---|---|---|
| `name` | yes | URL-safe identifier; uniqueness enforced on registration. |
| `url_template` | yes | `str.format`-compatible template — `{id}`, `{slug}`. |
| `queryset_factory` | yes | Zero-arg callable returning a fresh queryset on each request. |
| `fields` | optional | `{template_arg: dotted_orm_path}` — e.g. `{"brand_slug": "brand.slug"}`. |
| `lastmod_field` | optional | Dotted ORM path; omit to skip `<lastmod>` entirely. |
| `cursor_fields` | yes | Tuple of ORM field names used for keyset pagination. Must match the table's index prefix. |
| `order` | yes | Comma-separated Django `order_by` args, e.g. `-last_seen_at,-id`. |
| `page_size` | optional | Default 50 000 (Google's per-sitemap cap). |
| `enabled` | optional | Set `False` to keep registration but hide from index/feed. |

## Keyset pagination

The module never uses `OFFSET`. For a queryset ordered by `(last_seen_at
DESC, id DESC)`, the cursor is a `(last_seen_at, id)` tuple and the
filter expands to:

```
WHERE (last_seen_at < c0)
   OR (last_seen_at = c0 AND id < c1)
```

Constant time per page regardless of total row count, given an index on
the cursor columns. Fetches `page_size + 1` rows to detect `has_more`
without a second `COUNT(*)`.

Cursors are opaque base64-JSON to the frontend — decode for debugging,
pass through verbatim for normal use.

## Quality filter — built into the queryset

The sitemap doesn't decide what's eligible — your manager does. Example:

```python
class VehicleQuerySet(models.QuerySet):
    def sitemap_eligible(self, lookback_days: int = 30):
        cutoff = timezone.now() - timedelta(days=lookback_days)
        return self.filter(
            status='active',
            is_available=True,
            last_seen_at__gte=cutoff,
            photos__isnull=False,
        ).only('id', 'last_seen_at').distinct()
```

Rationale: with a 2M-row table, sending Google every active row is
counter-productive. Drop sold listings, stale rows, and photo-less items
to focus crawl budget on URLs that actually deserve to rank.

## Caching

Three TTL layers — set by SitemapConfig, enforced by Redis and HTTP
`Cache-Control`:

| Layer | TTL fresh | Knob |
|---|---|---|
| Redis (`sitemap:index:<v>`) | 300 s | `cache_index_seconds` |
| Redis (`sitemap:feed:<src>:<cursor-hash>:<v>`) | 3600 s | `cache_feed_seconds` |
| HTTP `Cache-Control: s-maxage=<ttl>, swr=<ttl*24>` | matches above | (derived) |

To bust everything globally without `FLUSHDB`, bump `cache_version`:

```python
from django_cfg.modules.django_sitemap import set_sitemap_config, SitemapConfig
set_sitemap_config(SitemapConfig(cache_version="v2"))
```

## Frontend integration (Next.js)

The frontend turns the JSON into XML using Next's built-in `sitemap.ts`
metadata file convention. Sketch (full code lives in your app, not in
this module):

```ts
// app/sitemap.ts
export const revalidate = 3600;

export async function generateSitemaps() {
  const index = await fetch(`${API}/cfg/sitemap/index/`).then(r => r.json());
  return index.sources.flatMap((s: any) =>
    s.chunks.map((c: any, i: number) => ({
      id: `${s.name}--${i + 1}--${c.cursor_to ?? ''}`,
    })),
  );
}

export default async function sitemap({ id }: { id: string }) {
  const [source, , cursor] = id.split('--');
  const params = new URLSearchParams({ source });
  if (cursor) params.set('cursor', cursor);
  const feed = await fetch(`${API}/cfg/sitemap/feed/?${params}`).then(r => r.json());
  return feed.entries.map((e: any) => ({
    url: `${HOST}${e.loc}`,
    lastModified: e.lastmod ? new Date(e.lastmod) : undefined,
  }));
}
```

`generateSitemaps()` makes Next emit `/sitemap/<id>.xml` per chunk plus
an auto-generated `<sitemapindex>` at `/sitemap.xml`. Pair with `robots.ts`
that points at `/sitemap.xml`.

## When NOT to use this module

- Sites under 1 000 URLs — `django.contrib.sitemaps` is fine.
- Static-only sites — write a flat `sitemap.xml` and stop thinking about
  it.
- You need per-locale `<xhtml:link rel="alternate">` — supported by Next
  but not currently emitted by this module; the contract has room to
  grow (`alternates: [{lang, loc}]`) when needed.

## Limits

- No image / video / news sitemap extensions yet.
- No `<priority>` or `<changefreq>` — Google ignores them; we omit on
  purpose. Re-add to `entries` if you find a non-Google crawler that
  needs them.
- Cursor encoding assumes JSON-serialisable cursor field values
  (datetime, date, str, int). Custom types — extend `cursors._jsonable`.

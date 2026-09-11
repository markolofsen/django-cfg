---
title: "@djangocfg/nextjs"
status: current
version: "1.0"
audience: frontend, agents
last_reviewed: 2026-09-11
---

# `@djangocfg/nextjs`

Next-only **server** utilities. Everything here is a subpath import — the root
does not re-export them.

| Subpath | For |
|---|---|
| `/sitemap` | `createDjangoSitemap`, `createSitemapIndex`, `tenantSources` — the Django-backed sitemap |
| `/og-image` | OG card generation |
| `/health` | Health endpoint |
| `/navigation` | Navigation helpers |
| `/config` | App config |
| `/pwa`, `/pwa/manifest`, `/pwa/worker`, `/worker` | PWA manifest and service worker |
| `/monitor` | Error reporting endpoint |
| `/ai` | AI route helpers |
| `/i18n`, `/i18n/server`, `/i18n/client`, `/i18n/proxy`, `/i18n/navigation`, `/i18n/routing`, `/i18n/request`, `/i18n/components` | `next-intl` wiring |

## What this workspace uses

Only the sitemap, in four files:

```ts
// app/sitemap.ts
import { createDjangoSitemap, tenantSources } from "@djangocfg/nextjs/sitemap";
// app/sitemap_index.xml/route.ts
import { createSitemapIndex, tenantSources } from "@djangocfg/nextjs/sitemap";
```

Both apps have their own. SEO rules for this workspace — canonical, robots,
redirects, OG cards — are in
[`../custom/seo-and-publication.md`](../custom/seo-and-publication.md); this page
only says which import provides them.

## Traps

- **This is not `@djangocfg/ui-core`.** Router *adapters* live in ui-core
  (`@djangocfg/ui-core/adapters/nextjs`); server utilities live here. Reaching
  into the wrong package for `<Link>` behaviour is the common confusion.
- **`/i18n/client` is a client entry, `/i18n/server` is not.** Importing the
  server one into a client component pulls `server-only` into the browser graph
  and fails the build with a message about the wrong file.

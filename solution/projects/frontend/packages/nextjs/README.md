<div align="center">

![@djangocfg/nextjs](https://raw.githubusercontent.com/markolofsen/assets/main/libs/djangocfg/nextjs.webp)

</div>

# @djangocfg/nextjs

> Server-side Next.js utilities: OG images, sitemap, health checks, i18n, PWA, navigation, and config

[![npm version](https://img.shields.io/npm/v/@djangocfg/nextjs.svg)](https://www.npmjs.com/package/@djangocfg/nextjs)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Part of [DjangoCFG](https://djangocfg.com)** — a modern Django framework for building production-ready SaaS applications. All `@djangocfg/*` packages are designed to work together, providing type-safe configuration, real-time features, and beautiful admin interfaces out of the box.

---

## Overview

`@djangocfg/nextjs` provides server-side utilities for Next.js applications built on top of Django-CFG.

> **Note:** Client components (legal pages, error pages, redirect components) are in `@djangocfg/layouts`.

## Features

- **Page Metadata + OG Images** — one factory for complete page metadata: titles, canonical + hreflang, OpenGraph, Twitter, icons (`@djangocfg/nextjs/og-image`)
- **i18n** — full next-intl integration with routing, middleware, and components
- **PWA** — zero-config service worker and manifest
- **Base Next.js Config** — reusable `createBaseNextConfig()` factory for monorepos
- **Security headers + CSP** — baseline Content-Security-Policy and hardening headers on every route, dev-aware (see below)
- **PWA** — manifest, viewport, icons, install prompt, how the pieces fit — see [`@docs/PWA_APP_SETUP.md`](./@docs/PWA_APP_SETUP.md)
- **Sitemap** — paginated sitemap-index backed by `django_cfg.modules.django_sitemap` (handles 2M+ URLs)
- **Health Checks** — production-ready health monitoring endpoints
- **Navigation** — route definitions, menu generation, and active-state helpers
- **AI Documentation** — search DjangoCFG docs via MCP server and CLI

## Installation

```bash
npm install @djangocfg/nextjs
# or
pnpm add @djangocfg/nextjs
# or
yarn add @djangocfg/nextjs
```

## Quick Start

### AI Documentation Search

Search DjangoCFG documentation from the terminal:

```bash
# CLI (works anywhere via npx)
npx @djangocfg/nextjs ai-docs search "database configuration"
npx @djangocfg/nextjs ai-docs mcp
```

Or use the TypeScript API:

```tsx
import { search, getDocs, getMcpConfig } from '@djangocfg/nextjs/ai';

// Search documentation
const results = await search('database configuration');
results.forEach(r => console.log(r.title, r.url));

// Get formatted docs
const docs = await getDocs('How to configure PostgreSQL?');

// Get MCP server config for AI assistants
const config = getMcpConfig();
```

### MCP Server for AI Assistants

Add to your AI assistant configuration:

```json
{
  "mcpServers": {
    "djangocfg-docs": {
      "url": "https://mcp.djangocfg.com/mcp"
    }
  }
}
```

### Base Next.js Configuration

Create a reusable base configuration for all your Next.js projects:

```tsx
// next.config.ts
import { createBaseNextConfig } from '@djangocfg/nextjs/config';
import bundleAnalyzer from '@next/bundle-analyzer';

const withBundleAnalyzer = bundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
});

export default withBundleAnalyzer(createBaseNextConfig({
  // Base path for static builds
  basePath: process.env.NEXT_PUBLIC_STATIC_BUILD === 'true' ? '/cfg/admin' : undefined,
  
  // Add custom transpile packages
  transpilePackages: ['my-custom-package'],
  
  // Custom webpack configuration (called after base webpack logic)
  webpack: (config, options) => {
    // Your custom webpack rules
    return config;
  },
}));
```

### Security headers & CSP

`createBaseNextConfig()` adds baseline security headers to **every route** out of
the box — no setup required:

- `Content-Security-Policy` — a pragmatic baseline that blocks the high-value
  injection vectors (`object-src 'none'`, `base-uri 'self'`, `form-action 'self'`,
  `frame-ancestors`) while keeping the inline/eval scripts a Next.js app needs.
  **Dev-aware:** `connect-src`/`img-src` allow `http:`/`ws:` in development (a
  local Django, plus any WebSocket transport the app brings itself) and tighten
  to `https:`/`wss:` only in production.
- `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`
- `X-Frame-Options: DENY` (or `SAMEORIGIN` when `allowIframeFrom` is set)

A fully strict nonce-based `script-src` is a planned follow-up (needs middleware +
per-request nonce). To allow iframe embedding, pass `allowIframeFrom: ['https://example.com']`.

### PWA (Progressive Web App)

**Zero-config PWA** - Works out of the box! Service worker and offline support included automatically.

#### 1. Create manifest

```tsx
// app/manifest.ts
import { createManifest, createScreenshots } from '@djangocfg/nextjs/config';
import { settings } from '@core/settings';

export default createManifest({
  name: settings.app.name,
  description: settings.app.description,
  themeColor: '#ffffff',
  backgroundColor: '#000000',
  icons: {
    logo192: settings.app.icons.logo192,
    logo384: settings.app.icons.logo384,
    logo512: settings.app.icons.logo512,
  },
  // Optional: Add screenshots for Richer PWA Install UI
  // IMPORTANT: Image dimensions must match sizes parameter!
  // screenshots: createScreenshots([
  //   '/screenshots/desktop-1920x1080.png',  // Wide: 1920x1080
  //   '/screenshots/mobile-390x844.png',     // Narrow: 390x844
  // ]),
});
```

#### 2. Add manifest metadata

```tsx
// app/layout.tsx
import { createManifestMetadata } from '@djangocfg/nextjs/config';

export const metadata = {
  ...createManifestMetadata({
    name: 'My App',
    themeColor: '#000000',
  }),
};
```

**That's it!** PWA is now enabled in production. Generated files:
- `/manifest.webmanifest` - From `app/manifest.ts`
- `/sw.js` - Service worker (auto-generated in production)
- `/workbox-*.js` - Workbox runtime

**Customization** (optional):

```tsx
// next.config.ts
export default createBaseNextConfig({
  pwa: {
    dest: 'public',
    disable: process.env.NODE_ENV === 'development', // Disable in dev
    fallbacks: {
      document: '/_offline', // Offline page
    },
    runtimeCaching: [
      // Custom caching rules
      ...defaultRuntimeCaching,
      createApiCacheRule('https://api.example.com'),
    ],
  },
});
```

See [PWA.md](./PWA.md) for complete guide.

### i18n (Internationalization)

Full next-intl integration for multilingual Next.js apps.

> **Important:** Use subpath imports to avoid React Context issues in server components:
> - `@djangocfg/nextjs/i18n` - Types only
> - `@djangocfg/nextjs/i18n/routing` - `routing`, `createRouting`, `generateLocaleParams`
> - `@djangocfg/nextjs/i18n/client` - `I18nProvider`, hooks
> - `@djangocfg/nextjs/i18n/components` - `LocaleSwitcher`

#### 1. Create middleware (proxy.ts)

```tsx
// proxy.ts (or middleware.ts)
import createMiddleware from 'next-intl/middleware';
import { routing } from '@djangocfg/nextjs/i18n/routing';

export default createMiddleware(routing);

export const config = {
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)',],
};
```

#### 2. Create i18n request config

```tsx
// i18n/request.ts
import { getRequestConfig } from 'next-intl/server';
import { en, ru, ko } from '@djangocfg/i18n/locales';
import { mergeTranslations } from '@djangocfg/i18n/utils';

const locales = {
  en: mergeTranslations(en, { app: appEn }),
  ru: mergeTranslations(ru, { app: appRu }),
  ko: mergeTranslations(ko, { app: appKo }),
};

export default getRequestConfig(async ({ requestLocale }) => {
  let locale = await requestLocale;
  if (!locale || !(locale in locales)) locale = 'en';

  return {
    locale,
    messages: locales[locale],
    timeZone: 'UTC',
  };
});
```

#### 3. Use in layout

```tsx
// app/[locale]/layout.tsx
import { getMessages } from 'next-intl/server';
import { I18nProvider } from '@djangocfg/nextjs/i18n/client';
import { routing, generateLocaleParams } from '@djangocfg/nextjs/i18n/routing';

export function generateStaticParams() {
  return generateLocaleParams();
}

export default async function LocaleLayout({ children, params }) {
  const { locale } = await params;
  const messages = await getMessages();

  return (
    <I18nProvider locale={locale} messages={messages}>
      {children}
    </I18nProvider>
  );
}
```

#### 4. Use translations in components

```tsx
'use client';
import { useTranslations } from 'next-intl';

function MyComponent() {
  const t = useTranslations('app');
  return <h1>{t('title')}</h1>;
}
```

#### Shared locale cookie (several hosts, one family)

`NEXT_LOCALE` is written by the **proxy** (`createProxy` → `shareLocaleCookie`) and by `useChangeLocale` in the browser, never during render. Server components read the locale from the URL segment, so the cookie cannot change what SSR renders; it only decides where a bare `/` redirects. With `Domain=<registrable domain>` every host of the family sends the same value; the host-only twin is expired so it cannot shadow it. Override the domain guess with `NEXT_PUBLIC_COOKIE_DOMAIN`.

What it costs, and the rules that keep SSR intact:
- A response that sets a cookie is not cached by a CDN by default. The proxy sets it only when next-intl wrote one (a bare-path visit or a switch), not on every page view; keep it that way and do not add `Set-Cookie` to static pages.
- Never read `NEXT_LOCALE` in a server component (`cookies()` makes the route dynamic). Take `locale` from `params`.
- SEO sites (one language per host, indexed) keep `localeCookie: false`; sharing applies only to app families behind a login.
- If this ever causes trouble, the fallback is no cookie at all: the locale lives in the URL, and the family switcher links to the sibling host with the same locale prefix.

#### Locale Switcher

Smart wrapper around `@djangocfg/layouts` LocaleSwitcher with automatic next-intl hooks:

```tsx
import { LocaleSwitcher } from '@djangocfg/nextjs/i18n/components';

// Basic usage (automatically gets locale from next-intl)
<LocaleSwitcher />

// With custom locales (override routing config)
<LocaleSwitcher locales={['en', 'ru']} />

// With custom labels and styling
<LocaleSwitcher
  labels={{ en: 'English', ru: 'Русский' }}
  variant="outline"
  size="sm"
/>
```

> **Note:** This component wraps `@djangocfg/layouts` LocaleSwitcher with `useLocaleSwitcher()` hook. For a presentational version that accepts locale data via props, use `LocaleSwitcher` from `@djangocfg/layouts` directly.

### Single sign-in host (optional)

One sign-in host (`auth.<apex>`) for all subdomains: `auth={{ sso: true }}` on `BaseApp` plus, to avoid the flash of a
protected page, this proxy/middleware. Off on `localhost`; the sign-in host itself never redirects.

```ts
// proxy.ts (or middleware.ts)
import { createSsoMiddleware } from '@djangocfg/nextjs/auth/middleware';

export const proxy = createSsoMiddleware({ protect: ['/private'], allow: ['/private/shared'] });
```

The host is `auth.` + the registrable domain of `NEXT_PUBLIC_SITE_URL` (override: `authHost` option or
`NEXT_PUBLIC_AUTH_HOST`). It checks only that the shared cookie exists; the API decides whether it is valid. Compose it
with the i18n proxy by returning its redirect first (see `apps/demo/proxy.ts`). Setup and the `next` rules: docs →
*One sign-in host for subdomains*.

### Sitemap Generation

Paginated sitemap-index integrated with `django_cfg.modules.django_sitemap`.
Backed by a typed JSON contract: Django streams keyset-paginated chunks,
Next.js's native `generateSitemaps()` turns each chunk into one XML file
plus an auto-generated `<sitemapindex>` at `/sitemap.xml`. Handles
catalogs up to Google's 50 000-URLs-per-file cap without materialising
data on the frontend.

```tsx
// app/sitemap.ts
import { createDjangoSitemap } from '@djangocfg/nextjs/sitemap';

const { generateSitemaps, sitemap } = createDjangoSitemap({
  host: process.env.NEXT_PUBLIC_SITE_URL!,
  apiUrl: process.env.NEXT_PUBLIC_API_URL,  // optional — omit for static-only
  staticRoutes: [
    { path: '/', changeFrequency: 'daily', priority: 1.0 },
    { path: '/catalog', changeFrequency: 'daily', priority: 0.9 },
  ],
});

export { generateSitemaps, sitemap as default };
export const revalidate = 3600;
```

```tsx
// app/robots.ts
import { createRobots } from '@djangocfg/nextjs/sitemap';

export default createRobots({
  host: process.env.NEXT_PUBLIC_SITE_URL!,
  disallow: ['/account/', '/auth', '/api/'],
});
```

See [`src/sitemap/README.md`](./src/sitemap/README.md) for the full
backend ↔ frontend integration guide, including the Django source
registration, cache layers, and deployment notes.

### Health Check Endpoint

Create a health monitoring endpoint:

```tsx
// app/healthz/route.ts
import { createHealthHandler } from '@djangocfg/nextjs/health';

export const GET = createHealthHandler({
  version: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
  checks: [
    {
      name: 'database',
      check: async () => {
        // Check database connection
        return await checkDatabase();
      },
    },
  ],
});
```

### Page Metadata + OG Images

One factory per app builds complete page `Metadata` (title, openGraph, twitter,
canonical + hreflang, icons). The OG image is chosen by a single `og` field —
the static brand image by default, or an exact URL:

```tsx
// app/_core/metadata.ts — bind once
import { makeMetadataFactory } from '@djangocfg/nextjs/og-image'
export const createMetadata = makeMetadataFactory({
  name: settings.app.name,
  description: settings.app.description,
  siteUrl: settings.app.siteUrl,
  ogImage: settings.app.media.ogimage,
  locales: LOCALES,
})

// landing page → static brand image (default)
export const metadata = createMetadata({ title: 'Pricing', path: '/pricing' })
// content page with its own image
export const metadata = createMetadata({ title: p.name, path, og: { image: p.image } })
```

For a card rendered per page, add an `opengraph-image` route — Next.js finds it
by filename and its output overrides whatever the factory set, so the factory
has no "dynamic" case of its own.

### Navigation Utilities

Define routes and generate navigation menus:

```tsx
import { defineRoute, routesToMenuItems } from '@djangocfg/nextjs/navigation';

const routes = [
  defineRoute('/dashboard', { title: 'Dashboard' }),
  defineRoute('/settings', { title: 'Settings' }),
];

const menuItems = routesToMenuItems(routes);
```

### Client Components

Client-side components (legal pages, error pages, redirect components) are available in `@djangocfg/layouts`:

```tsx
// Legal pages
import { PrivacyPage, TermsPage } from '@djangocfg/layouts/pages/legal';

// Error pages
import { ErrorLayout } from '@djangocfg/layouts/components/errors';

// Redirect component
import { RedirectPage } from '@djangocfg/layouts/components/RedirectPage';
```

## Exports

| Path | Description |
|------|-------------|
| `@djangocfg/nextjs` | Main exports (all modules) |
| `@djangocfg/nextjs/i18n` | **Types only** (safe for server components) |
| `@djangocfg/nextjs/i18n/routing` | `routing`, `createRouting`, `generateLocaleParams`, `DEFAULT_LOCALES`, `DEFAULT_LOCALE` |
| `@djangocfg/nextjs/i18n/client` | `I18nProvider`, hooks (`'use client'`) |
| `@djangocfg/nextjs/i18n/server` | Server-side i18n utilities |
| `@djangocfg/nextjs/i18n/components` | `LocaleSwitcher` (`'use client'`) |
| `@djangocfg/nextjs/i18n/proxy` | `createProxy` for middleware |
| `@djangocfg/nextjs/i18n/navigation` | `Link`, `redirect`, `usePathname`, `useRouter` |
| `@djangocfg/nextjs/auth` | Server-side shared session cookie: `serverAuthHeaders`, `getServerAccessToken`, `hasServerSession` |
| `@djangocfg/nextjs/auth/middleware` | `createSsoMiddleware`: single sign-in host (signed-out visitor of a protected path goes to `auth.<apex>/auth?next=…` before any render; edge-safe) |
| `@djangocfg/nextjs/ai` | AI documentation search and MCP config |
| `@djangocfg/nextjs/config` | Base Next.js configuration factory |
| `@djangocfg/nextjs/pwa` | PWA client utilities (service worker registration) |
| `@djangocfg/nextjs/pwa/worker` | Service worker creation helpers |
| `@djangocfg/nextjs/sitemap` | Sitemap generation with i18n hreflang support |
| `@djangocfg/nextjs/health` | Health check handlers |
| `@djangocfg/nextjs/og-image` | Page metadata factory — titles, canonical + hreflang, OpenGraph, Twitter, icons |
| `@djangocfg/nextjs/navigation` | Route definitions, menu generation, navigation helpers |

## API Reference

### Base Configuration

#### `createBaseNextConfig(options)`

Creates a reusable base Next.js configuration with standard DjangoCFG settings.

```tsx
createBaseNextConfig({
  basePath?: string;                    // Base path for static builds
  transpilePackages?: string[];          // Additional packages to transpile
  optimizePackageImports?: string[];     // Additional packages to optimize
  webpack?: (config, options) => config; // Custom webpack configuration
  experimental?: NextConfig['experimental']; // Custom experimental options
  env?: Record<string, string>;         // Custom environment variables
  // ... any other NextConfig options
})
```

**Features:**
- Automatic dev/production optimizations
- Filesystem caching for faster rebuilds
- Compression plugins for static builds (Gzip + Brotli)
- Standard transpile packages for monorepo
- Type-safe configuration merging

### i18n

> **Subpath imports required** - see table below for correct import paths.

#### `DEFAULT_LOCALES` / `DEFAULT_LOCALE`

All 17 supported locales and the default locale constant.

```tsx
import { DEFAULT_LOCALES, DEFAULT_LOCALE } from '@djangocfg/nextjs/i18n/routing';

DEFAULT_LOCALES  // ['en', 'ru', 'ko', 'ja', 'de', 'fr', 'zh', 'it', 'es', 'nl', 'ar', 'tr', 'pt-BR', 'pl', 'sv', 'no', 'da']
DEFAULT_LOCALE   // 'en'
```

Use in `locales.config.ts` to stay in sync with the package:

```ts
// i18n/locales.config.ts
export { DEFAULT_LOCALES as LOCALES, DEFAULT_LOCALE } from '@djangocfg/nextjs/i18n/routing';
export type { LocaleCode as AppLocale } from '@djangocfg/nextjs/i18n';
```

#### `routing`

Default routing configuration with all 17 locales and default locale `'en'`.

```tsx
import { routing } from '@djangocfg/nextjs/i18n/routing';

routing.locales       // ['en', 'ru', 'ko', 'ja', ...]
routing.defaultLocale // 'en'
```

#### `createRouting(config?)`

Create custom routing configuration.

```tsx
import { createRouting } from '@djangocfg/nextjs/i18n/routing';

const routing = createRouting({
  locales: ['en', 'de', 'fr'],
  defaultLocale: 'en',
  localePrefix: 'always', // 'always' | 'as-needed' | 'never'
});
```

#### `I18nProvider`

Provider component for next-intl integration (client component).

```tsx
import { I18nProvider } from '@djangocfg/nextjs/i18n/client';

<I18nProvider locale="en" messages={messages}>
  {children}
</I18nProvider>
```

Pass `locales` (the set the app ships) so `useLocales()` / `useLocaleSwitcher()` report it; without it they fall back to the built-in 17-locale list.


#### `LocaleSwitcher`

Smart locale switcher that wraps `@djangocfg/layouts` LocaleSwitcher with next-intl hooks.

```tsx
import { LocaleSwitcher } from '@djangocfg/nextjs/i18n/components';

// Automatically gets locale from next-intl routing
<LocaleSwitcher />

// With custom options
<LocaleSwitcher
  locales={['en', 'ru']}        // Override available locales
  labels={{ en: 'EN', ru: 'RU' }} // Custom locale labels
  variant="outline"
  size="sm"
  showIcon={true}
  className="w-full"
/>
```

**Props** (extends `@djangocfg/layouts` LocaleSwitcherProps):
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `locales` | `string[]` | From routing | Override available locales |
| `labels` | `Record<string, string>` | Built-in | Custom locale labels |
| `showCode` | `boolean` | `false` | Show locale code with label |
| `variant` | `'ghost' \| 'outline' \| 'default'` | `'ghost'` | Button variant |
| `size` | `'sm' \| 'default' \| 'lg' \| 'icon'` | `'sm'` | Button size |
| `showIcon` | `boolean` | `true` | Show globe icon |

### Sitemap

#### `createSitemapHandler(options)`

Creates a Next.js route handler for sitemap generation with optional i18n support.

```tsx
createSitemapHandler({
  siteUrl: string;
  staticPages?: SitemapUrl[];
  dynamicPages?: SitemapUrl[] | (() => Promise<SitemapUrl[]>);
  cacheControl?: string;
  // i18n support
  i18n?: {
    locales: string[];      // e.g., ['en', 'ru', 'ko']
    defaultLocale: string;  // e.g., 'en'
  };
})
```

When `i18n` is provided:
- URLs are expanded for each locale (e.g., `/about` → `/en/about`, `/ru/about`, `/ko/about`)
- `xhtml:link` elements with `hreflang` are added for SEO
- `x-default` points to the default locale

### Health

#### `createHealthHandler(config)`

Creates a health check route handler.

```tsx
createHealthHandler({
  version?: string;
  checks?: Array<{ name: string; check: () => Promise<boolean> }>;
  customData?: Record<string, any>;
})
```

### Page Metadata + OG Image

`@djangocfg/nextjs/og-image` builds complete page metadata: title templating,
canonical + hreflang alternates, OpenGraph, Twitter cards and icons.

See [`src/og-image/README.md`](./src/og-image/README.md) for full docs (the `og`
axis, `SiteMetaConfig`/`PageMeta` fields).

#### `makeMetadataFactory(config)` — recommended

Binds a `SiteMetaConfig` once; returns a per-page factory. The OG image is set by
the single `og` field: `'static'` (default) · `{ image, alt? }`.

```tsx
import { makeMetadataFactory } from '@djangocfg/nextjs/og-image'

export const createMetadata = makeMetadataFactory({
  name: 'CMDOP', description: '…', siteUrl: 'https://cmdop.com',
  ogImage: '/static/ogimage.png', locales: LOCALES,
})

export const metadata = createMetadata({ title: 'About', path: '/about' })      // brand image
export const metadata = createMetadata({ title: p.name, og: { image: p.image } })
```

#### Per-page rendered cards

Use Next.js's `opengraph-image` file convention — but note it applies only when
metadata leaves `openGraph.images` unset. `createMetadata` always sets it, so
the route is suppressed unless the page strips that key from the metadata the
factory returned. See [`src/og-image/README.md`](./src/og-image/README.md#per-page-cards).

#### Low-level (escape hatches)

`resolveOgImage(spec, staticUrl, fallbackTitle)` is the `OgSpec` decision point;
`extractTitle(metadata)` reads a plain title out of Next.js's title shapes. Most
pages use `createMetadata` and never touch these.

### Navigation

#### `defineRoute(path, metadata, config?)`

Defines a route with metadata.

```tsx
defineRoute('/dashboard', {
  title: 'Dashboard',
  description: 'Dashboard overview',
}, {
  basePath: '/admin',
  isStaticBuild: false,
})
```

#### `isActive(current, target, allRoutes?)`

Checks if a route is currently active.

```tsx
isActive('/admin/dashboard', '/admin/dashboard') // true
isActive('/admin/dashboard/settings', '/admin/dashboard') // true
isActive('/admin/dashboard', '/admin/settings') // false
```

#### `routesToMenuItems(routes)`

Converts route definitions to menu items.

```tsx
const menuItems = routesToMenuItems(allRoutes);
```


## Requirements

- Next.js >= 13.0.0 (App Router)
- React >= 18.0.0
- TypeScript >= 5.0.0

## Peer Dependencies

- `next` - Next.js framework (^15.5.7)

## Documentation

Full documentation available at [djangocfg.com](https://djangocfg.com)

## Contributing

Issues and pull requests are welcome at [GitHub](https://github.com/markolofsen/django-cfg)

## License

MIT - see [LICENSE](./LICENSE) for details

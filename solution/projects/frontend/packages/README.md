# @djangocfg Packages

Internal packages for the DjangoCFG monorepo.

## Packages

| Package | Description |
|---------|-------------|
| **@djangocfg/analytics** | Pageviews, sessions, and authenticated-user attribution — one route listener, N transports (self-hosted + GA4) |
| **@djangocfg/api** | Orval-generated TypeScript REST operations, React Query v5 hooks/query keys, Zod validation, and MSW handlers |
| **@djangocfg/devtools** | Error/console capture with backend ingest, plus a floating debug panel |
| **@djangocfg/eslint-config** | Shared ESLint configuration |
| **@djangocfg/i18n** | Internationalization with next-intl integration |
| **@djangocfg/layouts** | Layout system, navigation, user menus |
| **@djangocfg/nextjs** | Next.js server utilities (sitemap, health, OG images, contact forms, navigation, config) |
| **@djangocfg/payments** | Provider-agnostic React payments module (Stripe-first) |
| **@djangocfg/realtime** | Browser half of django-cfg realtime: one lazy WebSocket per tab, `useTopic`, replay and refetch-on-gap, a debug panel, an in-memory mock server |
| **@djangocfg/typescript-config** | Shared TypeScript configuration |
| **@djangocfg/ui-core** | React UI components (shadcn-based, framework-agnostic; Next adapter at `/adapters/nextjs`) |
| **@djangocfg/ui-tools** | Heavy tools with lazy loading (see below) |
| **@nextra/seo-engine** | SEO/link engine for the Nextra docs apps (sitemap, llms.txt, link check). Private, not published. |

Self-contained product blocks live in [`../widgets/`](../widgets/), not here — a
widget may depend on a package, never the reverse.

| Widget | Description |
|---|---|
| **@djangocfg/widget-ogimage** | Open Graph cards for Next.js: one satori renderer plus the brand/content card fabrics every `opengraph-image` route calls |

Retired packages are kept out of the workspace under
[`@archive/`](@archive/README.md).

## @djangocfg/ui-tools

Advanced React tools with lazy loading support:

| Tool | Import | Description |
|------|--------|-------------|
| Gallery | `@djangocfg/ui-tools/gallery` | Image gallery with lightbox |
| Map | `@djangocfg/ui-tools/map` | MapLibre maps with markers, draw |
| Mermaid | `@djangocfg/ui-tools/mermaid` | Mermaid diagram renderer |
| Upload | `@djangocfg/ui-tools/upload` | Drag-drop file uploader |
| Tour | `@djangocfg/ui-tools/tour` | Onboarding tours with spotlight |
| JsonTree | main export | JSON tree viewer |
| PrettyCode | main export | Syntax highlighted code |
| VideoPlayer | main export | Video player (vidstack) |
| AudioPlayer | main export | Audio player (wavesurfer) |
| JsonSchemaForm | main export | JSON Schema forms (RJSF) |

## Publishing

From the monorepo root (`frontend/`), not from here — one publisher covers
`packages/*` (one synced version) and `widgets/*` (independent versions):

```bash
make list                 # local vs npm
make plan BUMP=auto       # what would happen — touches nothing
make publish BUMP=patch   # bump, build, publish everything
```

Details: `scripts/publish/cli.mjs --help` and `PACKAGES_STRATEGY.md`.

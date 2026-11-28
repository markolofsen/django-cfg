# scripts/seo — universal Nextra 4 docs SEO toolkit

Brand-agnostic link-integrity + sitemap tooling for any **Nextra 4** (`content/`
app-router) docs app. Copy this whole folder between projects unchanged — the
only per-project file lives **outside** it (`seo.config.ts` in the app root).

## Layout

```
scripts/seo/
  cli.ts              # commander entry (sitemap | check | external | fix)
  index.ts            # programmatic API barrel
  core/               # brand-agnostic building blocks
    config.ts         #   loadConfig() — reads ../../seo.config.{ts,mjs,js,json}
    types.ts          #   shared types (NextraSeoConfig, LinkRef, …)
    routes.ts         #   content tree → route index (+ heading anchors)
    extract.ts        #   mdast link/image/heading/external extraction
  commands/           # one file per CLI verb
    check.ts          #   offline: pages + #anchors + images + jsx-relative-href
    external.ts       #   network: HEAD→GET probe of outbound http(s) URLs
    sitemap.ts        #   sitemap.xml + robots.txt
    fix.ts            #   auto-apply safe suggestions
  reporters/
    report.ts         #   human-readable check / external reports
```

## What `check` validates (offline, CI-friendly — exit 1 on any break)

- **pages** — `[..](/x)`, `./x`, `../x`, `/docs/x`; relative resolve from the file's folder.
- **#anchors** — fragment must match a heading slug (`github-slugger`, the exact
  algo Nextra uses) or an explicit `id=` / `{#id}` on the target page.
- **images** — `![](…)`, `<img src>`, `<Image src>` must exist under `public/`.
- **jsx-relative-href** — a *relative* `href`/`src` in a JSX/HTML element
  (`<Card>`, `<a>`, `<img>`) is flagged + auto-fixed to absolute. Nextra rewrites
  relative *markdown* links at build but leaves JSX attrs verbatim, so the browser
  mis-resolves them → 404. **In JSX always use absolute paths.**

`external` (separate, network) probes outbound URLs; 401/403/429 are reported but
not failed (bot-protection ≠ dead).

## Use it in a new project

1. Copy `scripts/seo/` into the app.
2. Add `seo.config.ts` in the app root:
   ```ts
   import type { NextraSeoConfig } from './scripts/seo';
   const config: Partial<NextraSeoConfig> = {
     name: 'myapp-docs-seo',
     baseUrl: 'https://docs.myapp.com',
   };
   export default config;
   ```
3. Add scripts (run via `tsx`, no build step) + devDeps:
   ```json
   "scripts": {
     "sitemap": "tsx scripts/seo/cli.ts sitemap",
     "check:links": "tsx scripts/seo/cli.ts check",
     "check:external": "tsx scripts/seo/cli.ts external",
     "fix:links": "tsx scripts/seo/cli.ts fix --write"
   }
   ```
   devDeps: `tsx commander fast-glob picocolors github-slugger unist-util-visit`
   `mdast-util-from-markdown mdast-util-mdx mdast-util-to-string`
   `micromark-extension-mdxjs @types/mdast`.

Per-command overrides: `--content`, `--public`, `--base-url`, `--config`,
`--concurrency`, `--timeout`.

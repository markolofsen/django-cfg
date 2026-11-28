/**
 * Broken-reference detection (offline). Validates three classes:
 *
 *  1. Page links  — `[..](/x)`, `./x`, `../x`, `/docs/x` …
 *       valid when they resolve to an existing route in the content tree.
 *  2. Anchors     — the `#frag` part of a page link (or a same-page `#frag`)
 *       valid when the target page exposes that heading slug (github-slugger,
 *       the same algorithm Nextra uses) or an explicit `id=`/`{#id}`.
 *  3. Images/assets — `![](..)`, `<img src>`, `<Image src>`
 *       valid when the path exists under `public/`.
 *
 * External (http:, mailto:, //…) refs are NOT checked here — use `external`.
 *
 * Classification of broken page links:
 *   - old-prefix     : /docs/X where /X (prefix stripped) is a real route
 *   - absolute-wrong : /slug missing, but exactly one route ends with that slug
 *   - missing-page   : no route and no unique relocation candidate
 *   - bad-anchor     : page resolves but the #fragment slug doesn't exist
 *   - missing-asset  : image path not found under public/
 */
import { posix } from 'node:path';
import { existsSync } from 'node:fs';
import { join, resolve } from 'node:path';
import fg from 'fast-glob';
import { extractLinks, extractHeadings, extractComponentHrefs, isExternal } from '../core/extract.js';
import { buildRouteIndex, discoverRoutes } from '../core/routes.js';
import type { BrokenLink, CheckResult, LinkRef, NextraSeoConfig, RouteInfo } from '../core/types.js';

const ASSET_EXT_RE = /\.[a-z0-9]{2,5}$/i; // .png, .svg, .pdf, .json, etc.

/** Resolve an authored pathname to a candidate route, given the file it lives in. */
function resolvePathname(link: LinkRef, contentRoot: string): string | null {
  let p = link.pathname;
  if (p === '') return null; // pure anchor handled by caller
  if (p.startsWith('/')) {
    // root-based already
  } else {
    // Relative links resolve against the *directory* the file lives in on disk.
    // For `foo/index.mdx` (route `/foo`) that directory IS `/foo`; for `foo/bar.mdx`
    // (route `/foo/bar`) it is `/foo`. Deriving the base dir from the file path —
    // not from dirname(route) — keeps `./sibling` correct inside index pages.
    const relFile = link.file.slice(contentRoot.length + 1).split(/[\\/]/).join('/');
    const fileDir = posix.dirname(relFile); // '.' when the file is at content root
    const baseDir = fileDir === '.' ? '/' : '/' + fileDir;
    p = posix.normalize(posix.join(baseDir, p));
  }
  if (p.length > 1) p = p.replace(/\/+$/, '');
  return p;
}

/** The route a file lives in, used to resolve same-page (`#frag`) anchors. */
function ownRoute(file: string, routes: RouteInfo[]): string | null {
  const r = routes.find((x) => x.file === file);
  return r ? r.path : null;
}

export async function checkLinks(config: NextraSeoConfig): Promise<CheckResult> {
  const contentRoot = resolve(process.cwd(), config.contentDir);
  const publicRoot = resolve(process.cwd(), config.publicDir);
  const routes = await discoverRoutes(config);
  const { valid, bySlug, fileOf } = buildRouteIndex(routes);

  // basePath enforcement (e.g. '/docs'). Empty string disables the rule.
  const basePath = (config.basePath ?? '').replace(/\/+$/, '');

  /**
   * Enforce the raw-`<a>` basePath rule for an internal absolute href.
   * Returns a BrokenLink if it violates the rule, or null if OK / not applicable.
   *
   *  - href missing the basePath but resolving to a real route → `missing-basepath`
   *    (suggest the prefixed form). This is the raw-`<a>` bug class.
   *  - href starting with basePath → strip it and validate the remainder against
   *    routes (`/docs/intro` → `/intro` ∈ routes ⇒ OK; else `missing-page`).
   *
   * Only call for raw-`<a>` (inJsx) absolute internal hrefs when basePath is set.
   */
  function checkBasePath(link: LinkRef): BrokenLink | null {
    const p = link.pathname;
    if (p === basePath || p.startsWith(basePath + '/')) {
      // Already prefixed — validate the stripped path resolves to a real route.
      const stripped = p.slice(basePath.length) || '/';
      const normalized = stripped.length > 1 ? stripped.replace(/\/+$/, '') : stripped;
      if (valid.has(normalized)) return null; // correct + resolves → OK
      return { ...link, reason: 'missing-page', autoFixable: false };
    }
    // Internal absolute, but missing the basePath prefix → raw <a> will 404.
    const normalized = p.length > 1 ? p.replace(/\/+$/, '') : p;
    const exists = valid.has(normalized);
    return {
      ...link,
      reason: 'missing-basepath',
      suggestion: exists ? basePath + p + link.anchor : undefined,
      autoFixable: false, // never silently rewrite component/MDX source
    };
  }

  // Lazy per-route heading-slug cache (only pay for pages that get anchor-linked).
  const headingCache = new Map<string, Set<string>>();
  async function anchorsFor(route: string): Promise<Set<string> | null> {
    if (headingCache.has(route)) return headingCache.get(route)!;
    const file = fileOf.get(route);
    if (!file) return null;
    const slugs = await extractHeadings(file);
    headingCache.set(route, slugs);
    return slugs;
  }

  const files = await fg('**/*.{mdx,md}', {
    cwd: contentRoot,
    ignore: ['**/node_modules/**', ...config.ignore],
    absolute: true,
  });

  const broken: BrokenLink[] = [];
  let linkCount = 0;

  for (const file of files) {
    const links = await extractLinks(file);
    for (const link of links) {
      if (isExternal(link.raw)) continue; // external — handled by `external` cmd

      // ---- basePath rule for genuine raw <a> ABSOLUTE internal hrefs in MDX ----
      // A literal `<a href="/x">` in MDX is a real HTML anchor — NOT auto-prefixed
      // by Next — so under basePath it must be `/docs/x`. This is restricted to
      // raw `a` tags ONLY: component invocations like `<Card href="/x">` map to a
      // component (DocCard) that adds the prefix at runtime, so their source href
      // is correctly authored WITHOUT `/docs` (like next/link) — never flag those.
      // Relative JSX hrefs fall through to the jsx-relative-href rule below.
      if (basePath && link.jsxTag === 'a' && link.kind === 'link' && link.pathname.startsWith('/')) {
        linkCount++;
        const b = checkBasePath(link);
        if (b) broken.push(b);
        continue;
      }

      // ---- JSX/HTML relative href (./x, ../x) — Nextra does NOT rewrite these ----
      // A relative href in <Card>/<a>/<img> ships verbatim; the browser resolves it against the
      // current URL (which has no trailing slash), dropping the last segment → wrong page / 404.
      // (Markdown `[..](./x)` is exempt: Nextra rewrites those to absolute at build time.)
      if (link.inJsx && /^\.\.?\//.test(link.pathname)) {
        linkCount++;
        const abs = resolvePathname(link, contentRoot); // markdown-spec resolve = the intended absolute path
        const exists = abs != null && (link.kind === 'image'
          ? existsSync(join(publicRoot, abs.replace(/^\//, '')))
          : valid.has(abs));
        broken.push({
          ...link,
          reason: 'jsx-relative-href',
          // Only auto-fix to a target we can confirm exists; otherwise flag for review.
          suggestion: abs ? abs + link.anchor : undefined,
          autoFixable: !!abs && exists,
        });
        continue;
      }

      // ---- Images / assets: must exist under public/ ----
      if (link.kind === 'image') {
        linkCount++;
        // Only root-absolute or relative file paths point at public/; data: etc skipped above.
        const p = link.pathname;
        if (!p) continue;
        // Asset path is served from public/ root; strip leading slash.
        const rel = p.replace(/^\//, '');
        if (existsSync(join(publicRoot, rel))) continue;
        broken.push({ ...link, reason: 'missing-asset', autoFixable: false });
        continue;
      }

      // ---- Pure same-page anchor (#frag) ----
      if (link.pathname === '' && link.anchor) {
        linkCount++;
        const route = ownRoute(file, routes);
        if (!route) continue; // file not a route (shouldn't happen) — skip
        const slugs = await anchorsFor(route);
        const frag = link.anchor.slice(1);
        if (!slugs || slugs.has(frag)) continue;
        broken.push({ ...link, reason: 'bad-anchor', autoFixable: false });
        continue;
      }

      if (ASSET_EXT_RE.test(link.pathname)) continue; // non-image asset link (rare) — skip

      linkCount++;
      const resolved = resolvePathname(link, contentRoot);

      // ---- Page resolves: validate its anchor (if any) ----
      if (resolved && valid.has(resolved)) {
        if (link.anchor) {
          const slugs = await anchorsFor(resolved);
          const frag = link.anchor.slice(1);
          if (slugs && !slugs.has(frag)) {
            broken.push({ ...link, reason: 'bad-anchor', autoFixable: false });
          }
        }
        continue; // page OK
      }

      // ---- Page broken: classify ----
      const slug = (resolved ?? link.pathname).split('/').filter(Boolean).pop() ?? '';

      // `old-prefix` (strip `/docs`) applies ONLY to Nextra-managed / markdown
      // links (`!inJsx`), where `/docs/...` is a stale prefix. For raw `<a>`
      // (inJsx) the opposite holds — `/docs` is REQUIRED — and those are handled
      // by the basePath rule above, so never strip here.
      if (!link.inJsx && link.pathname.startsWith('/docs')) {
        const stripped = link.pathname.replace(/^\/docs/, '') || '/';
        const normalized = stripped.length > 1 ? stripped.replace(/\/+$/, '') : stripped;
        if (valid.has(normalized)) {
          broken.push({ ...link, reason: 'old-prefix', suggestion: normalized + link.anchor, autoFixable: true });
          continue;
        }
        const cands = bySlug.get(slug) ?? [];
        if (cands.length === 1) {
          broken.push({ ...link, reason: 'old-prefix', suggestion: cands[0] + link.anchor, autoFixable: true });
          continue;
        }
        broken.push({ ...link, reason: 'missing-page', autoFixable: false });
        continue;
      }

      const candidates = bySlug.get(slug) ?? [];
      if (candidates.length === 1) {
        if (candidates[0] === resolved) continue; // defensive no-op guard
        broken.push({ ...link, reason: 'absolute-wrong', suggestion: candidates[0] + link.anchor, autoFixable: true });
        continue;
      }

      broken.push({
        ...link,
        reason: 'missing-page',
        suggestion: candidates.length > 1 ? candidates.join(' | ') : undefined,
        autoFixable: false,
      });
    }
  }

  // ---- Component/app scan: raw <a href> in .tsx/.jsx must carry basePath ----
  // Only runs when basePath is configured. Conservative: only static literal
  // `<a href="/x">` are extracted (see extractComponentHrefs); helper/expression
  // hrefs — including the fixed DocCard/SiteFooter — are not flagged.
  let appScanned = 0;
  if (basePath) {
    const appFiles = await fg(config.appGlobs ?? [], {
      cwd: process.cwd(),
      ignore: ['**/node_modules/**', '**/.next/**'],
      absolute: true,
    });
    for (const file of appFiles) {
      appScanned++;
      const hrefs = await extractComponentHrefs(file);
      for (const link of hrefs) {
        if (isExternal(link.raw)) continue; // external scheme / protocol-relative
        if (!link.pathname.startsWith('/')) continue; // anchors, relative, query — skip
        linkCount++;
        const b = checkBasePath(link);
        if (b) broken.push(b);
      }
    }
  }

  return { scanned: files.length + appScanned, links: linkCount, broken };
}

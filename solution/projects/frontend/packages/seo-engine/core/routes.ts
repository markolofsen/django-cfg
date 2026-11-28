/**
 * Route discovery for Nextra 4 `content/` (app-router, root-based URLs, NO /docs prefix).
 *
 * Mapping rules:
 *   content/index.mdx              -> "/"
 *   content/intro/index.mdx        -> "/intro"
 *   content/intro/quickstart.mdx   -> "/intro/quickstart"
 *
 * `_meta.ts` is respected only for `display: 'hidden'` (route still valid, lower priority)
 * and `href` entries (external/alias targets — not file-backed, so not added as routes).
 */
import { stat } from 'node:fs/promises';
import { resolve, relative, sep } from 'node:path';
import fg from 'fast-glob';
import type { NextraSeoConfig, RouteInfo } from './types.js';

/** Convert a content-relative .mdx file path to a root-based route. */
export function fileToRoute(relPath: string): string {
  const posix = relPath.split(sep).join('/');
  const noExt = posix.replace(/\.mdx?$/i, '');
  // strip trailing /index or bare index
  const route = noExt === 'index' ? '/' : '/' + noExt.replace(/\/index$/i, '');
  return route === '/' ? '/' : route.replace(/\/+$/, '');
}

export async function discoverRoutes(config: NextraSeoConfig): Promise<RouteInfo[]> {
  const contentRoot = resolve(process.cwd(), config.contentDir);

  const files = await fg('**/*.{mdx,md}', {
    cwd: contentRoot,
    ignore: ['**/node_modules/**', ...config.ignore],
    dot: false,
  });

  const routes: RouteInfo[] = [];
  for (const rel of files) {
    const abs = resolve(contentRoot, rel);
    const route = fileToRoute(rel);
    let lastmod = new Date().toISOString();
    try {
      lastmod = (await stat(abs)).mtime.toISOString();
    } catch {
      /* keep default */
    }
    const depth = route === '/' ? 0 : route.split('/').length - 1;
    routes.push({
      path: route,
      file: abs,
      priority: route === '/' ? 1.0 : Math.max(0.3, 0.9 - depth * 0.1),
      changefreq: 'weekly',
      lastmod,
    });
  }

  // de-dup (e.g. foo.mdx + foo/index.mdx both -> /foo): keep first, stable order
  const seen = new Set<string>();
  const unique = routes.filter((r) => (seen.has(r.path) ? false : (seen.add(r.path), true)));
  unique.sort((a, b) => a.path.localeCompare(b.path));
  return unique;
}

/**
 * Build a lookup of valid route pathnames + a slug index for fix suggestions.
 * slugIndex maps a leaf slug (last path segment) -> list of full routes that own it.
 */
export interface RouteIndex {
  /** Set of every valid route pathname (no trailing slash; "/" for home). */
  valid: Set<string>;
  /** leaf-slug -> routes that end with that slug. */
  bySlug: Map<string, string[]>;
  /** route pathname -> absolute source file (for anchor/heading lookup). */
  fileOf: Map<string, string>;
}

export function buildRouteIndex(routes: RouteInfo[]): RouteIndex {
  const valid = new Set<string>();
  const bySlug = new Map<string, string[]>();
  const fileOf = new Map<string, string>();
  for (const r of routes) {
    valid.add(r.path);
    fileOf.set(r.path, r.file);
    if (r.path === '/') continue;
    const slug = r.path.split('/').pop()!;
    const arr = bySlug.get(slug) ?? [];
    arr.push(r.path);
    bySlug.set(slug, arr);
  }
  return { valid, bySlug, fileOf };
}

export function contentRelative(config: NextraSeoConfig, abs: string): string {
  return relative(resolve(process.cwd(), config.contentDir), abs);
}

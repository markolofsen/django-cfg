/**
 * PWA (Progressive Web App) Plugin — dependency-free.
 *
 * History: this used to wrap `@serwist/next`. Serwist is a **webpack** plugin,
 * and Next.js 16 defaults to Turbopack, which does not run webpack loaders and
 * chokes on serwist's `fileURLToPath(new URL(".", import.meta.url))` during
 * static tracing — failing the whole build even when PWA was never enabled
 * (the mere `require('@serwist/next')` reference was enough). Since no app in
 * this monorepo actually turned PWA on (`withPWA` is opt-in and unused), we
 * dropped serwist entirely.
 *
 * What remains:
 *   - `createManifest` (in `./manifest`) — the web app manifest, which Next.js
 *     supports natively via `app/manifest.ts`; needs no library at all.
 *   - `withPWA` — a thin, Turbopack-safe pass-through kept for API stability.
 *   - `getServiceWorkerTemplate` — a vanilla service worker you can drop into
 *     `app/sw.ts`, no framework runtime required.
 *
 * If you want a full precache/offline story back, wire a real service worker
 * (the template below, or Workbox) yourself — but do it in an app, not here, so
 * one app's PWA choice can't break every consumer's build.
 */

import type { NextConfig } from 'next';

export interface PWAPluginOptions {
  /**
   * Path to service worker source file (relative to project root).
   * @default 'app/sw.ts'
   */
  swSrc?: string;

  /**
   * Destination for the compiled service worker.
   * @default 'public/sw.js'
   */
  swDest?: string;

  /**
   * Disable PWA completely.
   * @default true in development / static export, false otherwise
   */
  disable?: boolean;

  /** Cache pages on navigation. Consumed by a custom SW, if any. @default true */
  cacheOnNavigation?: boolean;

  /** Reload the app when the device comes back online. @default true */
  reloadOnOnline?: boolean;
}

/**
 * Turbopack-safe PWA pass-through.
 *
 * This no longer injects a build plugin — Next.js's native manifest support
 * plus a hand-written `app/sw.ts` (see {@link getServiceWorkerTemplate}) cover
 * the PWA surface without a webpack-only dependency. Kept as a named export so
 * existing `withPWA(config)` / `createBaseNextConfig({ pwa })` call sites keep
 * type-checking and behave predictably (they return the config unchanged).
 *
 * @example
 * ```ts
 * import { createBaseNextConfig } from '@djangocfg/nextjs/config';
 * export default createBaseNextConfig({ pwa: { swSrc: 'app/sw.ts' } });
 * ```
 */
export function withPWA(
  nextConfig: NextConfig,
  _options: PWAPluginOptions = {}
): NextConfig {
  return nextConfig;
}

/**
 * Vanilla service-worker template — no library.
 *
 * Returns ready-to-use, framework-free service worker source. Copy it into
 * `app/sw.ts` (or generate it) if you want offline support. It uses only the
 * standard Service Worker + Cache APIs, so it builds under Turbopack with no
 * extra dependency.
 *
 * @example
 * ```ts
 * import { getServiceWorkerTemplate } from '@djangocfg/nextjs/config';
 * console.log(getServiceWorkerTemplate()); // → paste into app/sw.ts
 * ```
 */
export function getServiceWorkerTemplate(): string {
  return `/**
 * Service Worker (vanilla) — standard Cache + Fetch APIs, no library.
 */

/// <reference lib="webworker" />
// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare const self: any;

const CACHE = 'app-cache-v1';
const OFFLINE_URL = '/_offline';

// Precache the offline fallback on install.
self.addEventListener('install', (event: any) => {
  event.waitUntil(
    caches.open(CACHE).then((cache: Cache) => cache.addAll([OFFLINE_URL]))
  );
  self.skipWaiting();
});

// Drop stale caches on activate and take control immediately.
self.addEventListener('activate', (event: any) => {
  event.waitUntil(
    caches.keys().then((keys: string[]) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Network-first for navigations, with an offline fallback.
self.addEventListener('fetch', (event: any) => {
  const { request } = event;
  if (request.mode !== 'navigate') return;
  event.respondWith(
    fetch(request).catch(() =>
      caches.match(OFFLINE_URL).then((r: Response | undefined) => r ?? Response.error())
    )
  );
});
`;
}

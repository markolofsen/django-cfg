/**
 * Service Worker Utilities — vanilla, dependency-free.
 *
 * Was a Serwist wrapper; serwist is a webpack-only plugin incompatible with
 * Next.js 16's Turbopack, so this is now a hand-written service worker built on
 * the standard Service Worker + Cache APIs. Same `createServiceWorker(options)`
 * entry point, no library, Turbopack-safe.
 */

/// <reference lib="webworker" />

export interface ServiceWorkerOptions {
  /** Offline fallback URL. @default '/_offline' */
  offlineFallback?: string;
  /** Activate a new SW immediately instead of waiting. @default true */
  skipWaiting?: boolean;
  /** Take control of open clients immediately. @default true */
  clientsClaim?: boolean;
  /** Name of the runtime cache bucket. @default 'app-cache-v1' */
  cacheName?: string;
}

/**
 * Register a minimal offline-capable service worker.
 *
 * Network-first for navigations with an offline fallback page; stale caches are
 * cleared on activate. No precache manifest (that was a serwist build-time
 * injection) — add your own `cache.addAll([...])` in the install step if you
 * need assets precached.
 *
 * @example
 * ```ts
 * // app/sw.ts
 * import { createServiceWorker } from '@djangocfg/nextjs/worker';
 * createServiceWorker({ offlineFallback: '/_offline' });
 * ```
 */
export function createServiceWorker(options: ServiceWorkerOptions = {}): void {
  const {
    offlineFallback = '/_offline',
    skipWaiting = true,
    clientsClaim = true,
    cacheName = 'app-cache-v1',
  } = options;

  // `self` resolves to the DOM lib's `Window` when this file is compiled as part
  // of an app; inside a service worker it is really a ServiceWorkerGlobalScope.
  // Casting once here types every event handler below via the standard overloads.
  const sw = self as unknown as ServiceWorkerGlobalScope;

  sw.addEventListener('install', (event) => {
    event.waitUntil(
      caches.open(cacheName).then((cache) => cache.addAll([offlineFallback]))
    );
    if (skipWaiting) sw.skipWaiting();
  });

  sw.addEventListener('activate', (event) => {
    event.waitUntil(
      caches
        .keys()
        .then((keys) =>
          Promise.all(keys.filter((k) => k !== cacheName).map((k) => caches.delete(k)))
        )
        .then(() => {
          if (clientsClaim) return sw.clients.claim();
        })
    );
  });

  sw.addEventListener('fetch', (event) => {
    const { request } = event;
    if (request.mode !== 'navigate') return;
    event.respondWith(
      fetch(request).catch(() =>
        caches
          .match(offlineFallback)
          .then((r: Response | undefined) => r ?? Response.error())
      )
    );
  });
}

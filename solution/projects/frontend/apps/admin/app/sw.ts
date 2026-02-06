/**
 * Service Worker (Serwist)
 *
 * Modern PWA service worker using Serwist
 * Configured via @djangocfg/nextjs/pwa/worker
 */

import { settings } from '@core/settings';
import { createServiceWorker } from '@djangocfg/nextjs/pwa/worker';

createServiceWorker({
  offlineFallback: '/_offline',
});

/**
 * Service Worker (Serwist)
 *
 * Modern PWA service worker using Serwist
 * Configured via @djangocfg/nextjs/pwa/worker
 */

import { createServiceWorker } from '@djangocfg/nextjs/pwa/worker';
import { settings } from '@core/settings';

createServiceWorker({
  offlineFallback: '/_offline',
  enablePushNotifications: true,
  // notificationIcon: settings.app.icons.logo192,
  // notificationBadge: settings.app.icons.logo192,
  notificationIcon: 'https://djangocfg.com/static/logos/192x192.png',
  notificationBadge: 'https://djangocfg.com/static/logos/192x192.png',
});

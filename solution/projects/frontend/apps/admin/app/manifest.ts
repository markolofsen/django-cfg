/**
 * PWA Manifest
 *
 * Automatically generated from @djangocfg/nextjs
 * Configured via @core/settings
 */

import { settings } from '@core/settings';
import { createManifest, createScreenshots } from '@djangocfg/nextjs/pwa';

// Forced rebuild for PWA manifest update (gcm_sender_id removal)
export default createManifest({
  name: settings.app.name,
  shortName: settings.app.name,
  description: settings.app.description,
  themeColor: '#ffffff',
  backgroundColor: '#000000',
  icons: {
    logo192: 'https://djangocfg.com/static/logos/192x192.png',
    logo384: 'https://djangocfg.com/static/logos/384x384.png',
    logo512: 'https://djangocfg.com/static/logos/512x512.png',
    // logo192: settings.app.icons.logo192,
    // logo384: settings.app.icons.logo384,
    // logo512: settings.app.icons.logo512,
  },
  // Screenshots for Richer PWA Install UI
  screenshots: createScreenshots([
    'https://djangocfg.com/static/pwa/1920x1080.png', // Auto: wide (desktop), 1920x1080
    'https://djangocfg.com/static/pwa/390x844.png',   // Auto: narrow (mobile), 390x844
  ]),
  // Protocol handlers for deep linking
  protocol_handlers: [
    {
      protocol: 'web+djangocfg',
      url: '/protocol-handler?action=%s',
    },
  ],
});

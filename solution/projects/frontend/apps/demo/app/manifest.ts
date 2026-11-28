/**
 * PWA manifest — generated via @djangocfg/nextjs/pwa.
 */

// Import from the serwist-free `/pwa/manifest` subpath, NOT the `/pwa` barrel:
// the barrel re-exports the PWA config plugin, which references `@serwist/next`
// via `createRequire`. Turbopack statically traces that and fails to build
// serwist's `new URL(".", import.meta.url)`, breaking this route (and the app).
import { createManifest } from '@djangocfg/nextjs/pwa/manifest';
import type { MetadataRoute } from 'next';

import { settings } from './_core/settings';

const manifest: () => MetadataRoute.Manifest = createManifest({
  name: settings.app.name,
  shortName: 'djangocfg',
  description: settings.app.description,
  themeColor: '#ffffff',
  backgroundColor: '#000000',
  icons: {
    logo192: 'https://djangocfg.com/static/logos/192x192.png',
    logo384: 'https://djangocfg.com/static/logos/384x384.png',
    logo512: 'https://djangocfg.com/static/logos/512x512.png',
  },
});

export default manifest;

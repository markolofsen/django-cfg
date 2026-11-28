/**
 * @djangocfg/nextjs
 *
 * Next.js utilities and components: sitemap, health, OG images, legal pages, error pages
 */

// Sitemap
export * from './sitemap';

// Health
export * from './health';

// Navigation
export * from './navigation';

// Config
export * from './config';

// AI Documentation
export * from './ai';

// Types
export type * from './types';

// PWA worker utilities (separate export for tree-shaking)
// Import via: import { createServiceWorker } from '@djangocfg/nextjs/worker'
// Note: worker/ has its own package.json with "type": "module"


/**
 * Sitemap XML Route Handler
 *
 * Generates dynamic XML sitemap for SEO
 * Uses @djangocfg/nextjs sitemap utilities
 * 
 * Note: For static export builds, this route is marked as static to allow the build to complete.
 */

import { createSitemapHandler } from '@djangocfg/nextjs/sitemap';
import { settings } from '../_core/settings';
import { routes } from '../_routes/index';

// Mark as static for static export compatibility
export const dynamic = 'force-static';
export const revalidate = false;

// Get site URL from environment or settings
const siteUrl = settings.app.siteUrl;
// Get today's date in ISO format
const today = new Date().toISOString().split('T')[0];

// Create sitemap handler
const sitemapHandler = createSitemapHandler({
  siteUrl,
  staticPages: [
    // Home page
    {
      loc: routes.public.home.path,
      changefreq: 'daily',
      priority: 1.0,
      lastmod: today,
    },
    // Public pages
    {
      loc: routes.public.contact.path,
      changefreq: 'monthly',
      priority: 0.8,
      lastmod: today,
    },
    // Legal pages (lower priority)
    {
      loc: routes.public.privacy.path,
      changefreq: 'yearly',
      priority: 0.3,
      lastmod: today,
    },
    {
      loc: routes.public.terms.path,
      changefreq: 'yearly',
      priority: 0.3,
      lastmod: today,
    },
    {
      loc: routes.public.cookies.path,
      changefreq: 'yearly',
      priority: 0.3,
      lastmod: today,
    },
    {
      loc: routes.public.security.path,
      changefreq: 'yearly',
      priority: 0.3,
      lastmod: today,
    },
  ],
  dynamicPages: async () => {
    // Add dynamic pages here if needed
    // For example, if you have blog posts, products, etc.
    const dynamicUrls = [];

    // Example: Add admin dashboard pages (if you want them in sitemap)
    // Note: Usually admin pages are not included in public sitemap
    // Uncomment if needed:
    /*
    dynamicUrls.push({
      loc: routes.admin.overview.path,
      changefreq: 'daily',
      priority: 0.5,
      lastmod: today,
    });
    */

    return dynamicUrls;
  },
  cacheControl: 'public, s-maxage=86400, stale-while-revalidate',
});

// Export GET handler
export const GET = sitemapHandler;


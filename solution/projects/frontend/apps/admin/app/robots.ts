import { createRobots } from '@djangocfg/nextjs/sitemap';

import { settings } from './_core/settings';

// Index lives at /sitemap_index.xml (not /sitemap.xml) because Next.js
// reserves /sitemap.xml for app/sitemap.ts (the chunk factory), even
// when generateSitemaps() is used and the URL itself ends up 404.
const host = settings.app.siteUrl || process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';

export default createRobots({
  host,
  disallow: ['/api/', '/dashboard/'],
  sitemap: `${host}/sitemap_index.xml`,
});

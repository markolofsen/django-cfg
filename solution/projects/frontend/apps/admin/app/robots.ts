/**
 * Robots.txt Route
 *
 * Controls search engine crawler access
 * https://nextjs.org/docs/app/api-reference/file-conventions/metadata/robots
 */

import type { MetadataRoute } from 'next';
import { settings } from './_core/settings';

export default function robots(): MetadataRoute.Robots {
  const siteUrl = settings.app.siteUrl;

  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/api/', '/dashboard/'],
      },
    ],
    sitemap: siteUrl ? `${siteUrl}/sitemap.xml` : undefined,
  };
}

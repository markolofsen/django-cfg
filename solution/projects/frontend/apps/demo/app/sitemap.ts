/**
 * Sitemap — generated via @djangocfg/nextjs/sitemap.
 *
 * Static routes only; private pages stay out (they sit behind auth and
 * don't need to be indexed).
 */

import { createDjangoSitemap } from '@djangocfg/nextjs/sitemap';
import type { MetadataRoute } from 'next';

import { routes } from './_routes/public';

const { generateSitemaps, sitemap } = createDjangoSitemap({
  host: process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3010',
  apiUrl: process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000',
  staticRoutes: [
    { path: routes.home, changeFrequency: 'weekly', priority: 1.0 },
    { path: routes.auth, changeFrequency: 'monthly', priority: 0.3 },
    { path: routes.realtime, changeFrequency: 'monthly', priority: 0.5 },
    { path: routes.legal.privacy, changeFrequency: 'yearly', priority: 0.2 },
    { path: routes.legal.terms, changeFrequency: 'yearly', priority: 0.2 },
  ],
});

export { generateSitemaps };
const typedSitemap: (props: { id: Promise<string> }) => Promise<MetadataRoute.Sitemap> = sitemap;

export default typedSitemap;
export const revalidate = 3600;

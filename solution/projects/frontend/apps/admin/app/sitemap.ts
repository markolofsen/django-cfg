/**
 * Sitemap — generated via @djangocfg/nextjs/sitemap.
 *
 * Public, static routes only. Admin/private pages sit behind auth and
 * stay out of the index. Next.js serves this at `/sitemap.xml`.
 */

import { createDjangoSitemap } from '@djangocfg/nextjs/sitemap';

import { routes } from './_routes/index';

const { generateSitemaps, sitemap } = createDjangoSitemap({
  host: process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000',
  apiUrl: process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000',
  staticRoutes: [
    { path: routes.public.home.path, changeFrequency: 'daily', priority: 1.0 },
    { path: routes.public.privacy.path, changeFrequency: 'yearly', priority: 0.3 },
    { path: routes.public.terms.path, changeFrequency: 'yearly', priority: 0.3 },
    { path: routes.public.cookies.path, changeFrequency: 'yearly', priority: 0.3 },
    { path: routes.public.security.path, changeFrequency: 'yearly', priority: 0.3 },
  ],
});

export { generateSitemaps, sitemap as default };
export const revalidate = 3600;

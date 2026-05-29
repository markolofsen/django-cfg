import { createSitemapIndex } from '@djangocfg/nextjs/sitemap';

export const { GET } = createSitemapIndex({
  host: process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000',
  apiUrl: process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000',
});

export const revalidate = 600;

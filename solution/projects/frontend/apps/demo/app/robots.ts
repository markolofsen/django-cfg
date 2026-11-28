import { createRobots } from '@djangocfg/nextjs/sitemap';

export default createRobots({
  host: process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3010',
  disallow: ['/private/', '/auth', '/api/'],
});

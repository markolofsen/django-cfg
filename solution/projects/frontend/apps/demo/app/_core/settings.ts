export const isDevelopment = process.env.NODE_ENV === 'development';
export const isProduction = !isDevelopment;
export const isStaticBuild = process.env.NEXT_PUBLIC_STATIC_BUILD === 'true';

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3010';
const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';

export const settings = {
  app: {
    name: 'djangocfg demo',
    version: '1.0.0',
    description:
      'Minimal Next.js shell for django-cfg — auth, i18n, layouts, sitemap. UI primitives live in apps/storybook.',
    siteUrl,
    media: {
      favicon: '/favicon.png',
    },
  },

  isStaticBuild,

  api: {
    baseUrl: apiUrl,
  },
} as const;

export type Settings = typeof settings;

export const isDev = process.env.NODE_ENV === 'development';
export const isProd = !isDev;
export const isBrowser = typeof window !== 'undefined';

/**
 * Next.js static-export build (`output: 'export'`). Loggers treat it like dev
 * for visibility; some auth/SSR features behave differently under it.
 */
export const isStaticBuild = process.env.NEXT_PUBLIC_STATIC_BUILD === 'true';

/**
 * Next.js Proxy (i18n routing)
 * @see https://next-intl.dev/docs/routing/middleware
 */

import createMiddleware from 'next-intl/middleware';
import { routing } from '@djangocfg/nextjs/i18n';

const handleI18nRouting = createMiddleware(routing);

export default function proxy(request: Parameters<typeof handleI18nRouting>[0]) {
  return handleI18nRouting(request);
}

export const config = {
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)',],
};

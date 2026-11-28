/**
 * Next.js Proxy (i18n routing + optional single sign-in).
 * @see https://next-intl.dev/docs/routing/middleware
 */

import createMiddleware from 'next-intl/middleware';

import { createSsoMiddleware } from '@djangocfg/nextjs/auth/middleware';
import { routing } from '@djangocfg/nextjs/i18n/routing';

const handleI18nRouting = createMiddleware(routing);

// Only with NEXT_PUBLIC_SSO=true. Sends a signed-out visitor of `/private` to auth.<apex>/auth?next=… before any page renders
// (no flash); on localhost there is no apex, so it does nothing. The host (auth.<apex>) is derived from NEXT_PUBLIC_SITE_URL.
const sso = process.env.NEXT_PUBLIC_SSO === 'true' ? createSsoMiddleware({ protect: ['/private', '/admin'] }) : null;

export default function proxy(request: Parameters<typeof handleI18nRouting>[0]) {
  if (sso) {
    const res = sso(request);
    // A redirect is final; `next()` means "not mine, carry on".
    if (res.headers.get('location')) return res;
  }
  return handleI18nRouting(request);
}

export const config = {
  matcher: ['/((?!_next|_vercel|api/|.*\\..*).*)'],
};

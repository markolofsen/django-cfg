/**
 * Single sign-in for Next.js middleware (edge-safe: `next/server` only).
 *
 * ```ts
 * // middleware.ts of any app of the family
 * import { createSsoMiddleware } from '@djangocfg/nextjs/auth/middleware';
 * export const middleware = createSsoMiddleware({ protect: ['/private'] }) // host: auth.<apex of NEXT_PUBLIC_SITE_URL>;
 * export const config = { matcher: ['/((?!_next|api|.*\\..*).*)'] };
 * ```
 *
 * - On a follower host (`my.reforms.ai`), a request for a protected path without the shared session
 *   cookie is answered with a 307 to `https://reforms.ai/auth?next=<this URL>`: no page, no flicker.
 * - On the sign-in host, a visitor who already has a session and opens `/auth?next=…` is sent to
 *   the validated `next` right here.
 * - Off (passes everything) when `host` is empty, or the request is outside the apex (localhost).
 *
 * The cookie is only checked for presence: the API decides whether the token is valid, and the
 * client refreshes a stale one. Django never reads this cookie, so it is not an authenticator.
 */
import { NextResponse, type NextRequest } from 'next/server';

import {
  CFG_KEYS,
  SSO_ERROR,
  SSO_RETURN,
  buildSsoLoginUrl,
  deriveAuthHost,
  markReturn,
  resolveSso,
  safeNext,
} from '@djangocfg/api/storage';

export interface SsoMiddlewareOptions {
  /** Sign-in host. Default: `NEXT_PUBLIC_AUTH_HOST`, else `auth.<apex of NEXT_PUBLIC_SITE_URL>`; none of them (localhost) = middleware does nothing. */
  authHost?: string | undefined;
  /** Alias of `authHost`. */
  host?: string | undefined;
  /** Path prefixes that need a session (after the locale segment is stripped). Default `['/private']`. */
  protect?: string[];
  /** Prefixes inside `protect` that stay open. */
  allow?: string[];
  /** Sign-in page path on the host. Default `/auth`. */
  path?: string;
}

const stripLocale = (p: string) => p.replace(/^\/[a-z]{2}(?=\/|$)/, '') || '/';
const under = (path: string, prefixes: string[]) =>
  prefixes.some((p) => path === p || path.startsWith(p.endsWith('/') ? p : `${p}/`));

/** The URL the browser used: behind Traefik `request.url` is the container's, the forwarded headers are the visitor's. */
export function publicUrl(req: NextRequest): URL {
  const host = (req.headers.get('x-forwarded-host') || req.headers.get('host') || req.nextUrl.host).split(',')[0]!.trim();
  const proto = (req.headers.get('x-forwarded-proto') || req.nextUrl.protocol.replace(':', '')).split(',')[0]!.trim();
  return new URL(`${req.nextUrl.pathname}${req.nextUrl.search}`, `${proto}://${host}`);
}

export function hasSessionCookie(req: NextRequest): boolean {
  return Boolean(req.cookies.get(CFG_KEYS.accessToken.key)?.value || req.cookies.get(CFG_KEYS.refreshToken.key)?.value);
}

export function createSsoMiddleware(options: SsoMiddlewareOptions) {
  const protect = options.protect ?? ['/private'];
  const allow = options.allow ?? [];
  return function ssoMiddleware(req: NextRequest): NextResponse {
    const hostValue = options.authHost || options.host || process.env.NEXT_PUBLIC_AUTH_HOST || deriveAuthHost(process.env.NEXT_PUBLIC_SITE_URL);
    if (!hostValue) return NextResponse.next();
    const url = publicUrl(req);
    const state = resolveSso({ authHost: hostValue, path: options.path }, { hostname: url.hostname, protocol: url.protocol });
    if (!state.enabled) return NextResponse.next();

    const path = stripLocale(url.pathname);
    const signedIn = hasSessionCookie(req);

    if (state.isAuthHost) {
      if (signedIn && path === state.authPath && !url.searchParams.has('flow') && !url.searchParams.has(SSO_ERROR)) {
        const next = safeNext(url.searchParams.get('next'), state.apex, state.authPath);
        if (next) {
          const back = markReturn(next);
          return NextResponse.redirect(back.startsWith('/') ? new URL(back, url) : back);
        }
      }
      return NextResponse.next();
    }

    if (!signedIn && under(path, protect) && !under(path, allow)) {
      // Sent back by the host (`sso_ret`) and still no cookie: it never reached this host. Tell the host, do not loop.
      const target = buildSsoLoginUrl(state, url.href, url.searchParams.has(SSO_RETURN));
      if (target) return NextResponse.redirect(target);
    }
    return NextResponse.next();
  };
}

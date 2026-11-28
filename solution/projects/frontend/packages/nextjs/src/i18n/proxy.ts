/**
 * i18n Proxy for Next.js App Router (Next.js 16+)
 *
 * Handles locale detection and routing
 *
 * @example
 * ```ts
 * // proxy.ts
 * export { proxy as default, config } from '@djangocfg/nextjs/i18n';
 *
 * // Or with custom routing:
 * import { createProxy } from '@djangocfg/nextjs/i18n';
 * import { routing } from './i18n/routing';
 *
 * export default createProxy(routing);
 * export const config = { matcher: [...] };
 * ```
 */

import createIntlMiddleware from 'next-intl/middleware';

import { createRouting, routing } from './routing';
import { expireHostOnlyLocaleCookie, LOCALE_COOKIE, LOCALE_COOKIE_MAX_AGE, sharedCookieDomain } from './shared-locale';

import type { NextRequest, NextResponse } from 'next/server';

import type { I18nConfig } from './types';

// ─────────────────────────────────────────────────────────────────────────────
// Proxy Factory
// ─────────────────────────────────────────────────────────────────────────────

/**
 * next-intl writes `NEXT_LOCALE` host-only. Rewrite it onto the registrable domain, so the locale a reader chose on one host
 * of the family is the locale on all of them, and expire the host-only twin that would shadow it. A host that cannot share
 * (localhost, an IP) is left as next-intl wrote it. `NEXT_PUBLIC_COOKIE_DOMAIN` overrides the guess.
 */
export function shareLocaleCookie(request: NextRequest, response: NextResponse): NextResponse {
  const written = response.cookies.get(LOCALE_COOKIE);
  if (!written) return response;
  const host = request.headers.get('x-forwarded-host') ?? request.headers.get('host') ?? request.nextUrl.hostname;
  const domain = sharedCookieDomain(host, process.env.NEXT_PUBLIC_COOKIE_DOMAIN);
  if (!domain) return response;
  const secure = (request.headers.get('x-forwarded-proto') ?? request.nextUrl.protocol.replace(':', '')) === 'https';
  response.cookies.set({ name: LOCALE_COOKIE, value: written.value, domain, path: '/', maxAge: LOCALE_COOKIE_MAX_AGE, sameSite: 'lax', secure });
  response.headers.append('set-cookie', expireHostOnlyLocaleCookie(secure));
  return response;
}

/**
 * A host serves only the locales it declares, but the cookie is shared by every host of the family. next-intl rewrites a
 * cookie it cannot use to the locale it served, so one visit to an English-only host turned a reader's Russian back to
 * English on all the others. Hide such a cookie from next-intl: the host serves its own resolution and leaves the
 * reader's choice alone.
 */
export function keepForeignLocaleCookie(request: NextRequest, locales: readonly string[]): NextRequest {
  const value = request.cookies.get(LOCALE_COOKIE)?.value;
  if (value && !locales.includes(value)) request.cookies.delete(LOCALE_COOKIE);
  return request;
}

/**
 * Create i18n proxy handler with custom routing configuration
 */
export function createProxy(routingConfig?: ReturnType<typeof createRouting>) {
  const config = routingConfig ?? routing;
  const intl = createIntlMiddleware(config);
  return (request: NextRequest) =>
    shareLocaleCookie(request, intl(keepForeignLocaleCookie(request, config.locales)) as NextResponse);
}

/**
 * Create i18n proxy from config options
 */
export function createProxyFromConfig(config: Partial<I18nConfig>) {
  return createProxy(createRouting(config));
}

// ─────────────────────────────────────────────────────────────────────────────
// Default Proxy
// ─────────────────────────────────────────────────────────────────────────────

const handleI18nRouting = createProxy();

/**
 * Default proxy function using default routing
 *
 * @example
 * ```ts
 * // proxy.ts
 * export { proxy as default, config } from '@djangocfg/nextjs/i18n';
 * ```
 */
export function proxy(request: NextRequest) {
  return handleI18nRouting(request);
}

// ─────────────────────────────────────────────────────────────────────────────
// Config
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Default proxy config
 * Matches all paths except static files, API routes, and Next.js internals
 *
 * Uses explicit _next/static and _next/image exclusions (required for Next.js 16 / Turbopack)
 *
 * @example
 * ```ts
 * // proxy.ts
 * export { proxy as default, config } from '@djangocfg/nextjs/i18n';
 * ```
 */
export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)',
  ],
};

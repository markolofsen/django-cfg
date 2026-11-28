/**
 * Environment Variable Utilities
 */

import consola from 'consola';

export const isStaticBuild = process.env.NEXT_PUBLIC_STATIC_BUILD === 'true';
export const isDev = process.env.NODE_ENV === 'development';
export const isProduction = !isDev;
export const isCI = process.env.CI === 'true';

export function getBasePath(): string {
  return isStaticBuild ? '/cfg/nextjs-admin' : '';
}

/**
 * Resolve the API origin that gets inlined into the client bundle.
 *
 * `NEXT_PUBLIC_*` is substituted at BUILD time, so a value supplied only at
 * container runtime (a compose `environment:` entry, a `docker run -e`) arrives
 * far too late — the bundle already shipped with whatever was present during
 * `next build`.
 *
 * An empty result means "no API origin is configured". Callers MUST treat that
 * as *do not send the request* rather than falling back to a relative path: the
 * browser resolves a relative URL against the CURRENT page, so on an
 * i18n-prefixed route `/cfg/accounts/profile` silently becomes
 * `https://site.com/<locale>/cfg/accounts/profile` — a 404 that reproduces only
 * in production. Use {@link hasApiUrl} to gate those call sites.
 *
 * The one case where empty legitimately means "relative": a static build served
 * from the same origin as Django.
 */
export function getApiUrl(): string {
  return isStaticBuild ? '' : (process.env.NEXT_PUBLIC_API_URL || '');
}

/**
 * Whether a usable API origin is configured for this build.
 *
 * Gate every network call that targets Django on this. An app with no backend
 * (a pure marketing site) then needs no configuration at all — its optional
 * transports simply stay dormant instead of firing requests at the page's own
 * origin.
 *
 * A static build is same-origin by design, so relative paths ARE the intent
 * there and this reports true despite the empty string.
 */
export function hasApiUrl(): boolean {
  return isStaticBuild || Boolean(process.env.NEXT_PUBLIC_API_URL);
}

/**
 * Warn once, at build time, when no API origin is configured.
 *
 * Not an error: an app with no backend is a legitimate configuration. But the
 * same empty value also appears when a build *should* have had an API URL and
 * lost it — a `.dockerignore` rule stripping `.env.production`, or a value
 * supplied only through a runtime `environment:` entry. Both produce a bundle
 * whose API-backed features are silently inert, so say so while the build log
 * is still being read.
 */
export function warnIfApiUrlMissing(): void {
  if (hasApiUrl() || isDev) return;

  consola.warn(
    'NEXT_PUBLIC_API_URL is not set — API-backed features are disabled in this build.\n' +
      'Requests that need it are skipped rather than sent to a relative path.\n' +
      'If this app DOES have a backend, the value must be present at BUILD time:\n' +
      '  • commit it to the app\'s `.env.production`, and check no `.dockerignore`\n' +
      '    rule (e.g. `**/.env*`) strips that file from the build context;\n' +
      '  • or pass it as a Dockerfile ARG/ENV before the build step.\n' +
      'A compose `environment:` entry is too late — it only exists at runtime.',
  );
}

export function getSiteUrl(): string {
  return isStaticBuild ? '' : (process.env.NEXT_PUBLIC_SITE_URL || '');
}

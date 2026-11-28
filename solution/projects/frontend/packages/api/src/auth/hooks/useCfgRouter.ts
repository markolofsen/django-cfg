/**
 * Universal Router Hook with BasePath Support
 *
 * Wrapper around Next.js useRouter that automatically handles basePath
 * for static builds served via iframe or subdirectory
 * 
 * IMPORTANT: In Next.js 15 App Router, router.push() does NOT automatically
 * handle basePath (unlike Pages Router). This is a breaking change in App Router.
 * 
 * This hook ensures basePath is always included when navigating, especially
 * important for static exports served via iframe where basePath is critical.
 * 
 * @see https://nextjs.org/docs/app/building-your-application/upgrading/app-router-migration
 */

'use client';

import { useRouter as useNextRouter } from 'next/navigation';
import { useCallback, useMemo } from 'react';

import { authTrace } from '../trace';
import { buildSsoLoginUrl, currentNextUrl, getSsoState, hasReturnMarker, isAuthRoute, safeNext } from '../utils/sso';

/** `{ next: false }`: go to the sign-in host without a way back (sign-out). */
export interface CfgNavOptions {
  next?: false;
}

/**
 * With single sign-in on, a follower host's own sign-in route is not rendered: the visitor goes to
 * `{authHost}/auth?next=<this page>`. Null = not an SSO hop, navigate as asked. This is the one
 * place every guard, redirect page, session-expiry and logout path goes through.
 */
function ssoHop(href: string, opts?: CfgNavOptions): string | null {
  const state = getSsoState();
  if (!state.enabled || state.isAuthHost || !isAuthRoute(href, state.authPath)) return null;
  if (opts?.next === false) return buildSsoLoginUrl(state, null);
  const q = href.includes('?') ? new URLSearchParams((href.split('?')[1] ?? '').split('#')[0]).get('next') : null;
  const asked = q ? safeNext(q, state.apex, state.authPath) : null;
  const here = currentNextUrl();
  // Sent back by the host a moment ago and still signed out: the shared cookie did not reach this host. Say so, do not bounce again.
  return buildSsoLoginUrl(state, asked ?? here, hasReturnMarker(here));
}

const ABSOLUTE = /^[a-z][a-z0-9+.-]*:/i;

/**
 * A hard navigation unloads the page. Once one is in flight, a second one (two 401s, the guard and an effect, a double
 * click) is dropped: the first decides. Reset when the page is restored from the back/forward cache.
 */
let hardNavigating = false;
if (typeof window !== 'undefined') {
  window.addEventListener('pageshow', (e) => {
    if (e.persisted) hardNavigating = false;
  });
}

function fromPath(): string {
  return typeof window === 'undefined' ? '' : window.location.pathname;
}

/**
 * Get base path from environment variable. Only the literal read is inlined by Next; a `typeof process` gate in
 * front of it would return '' in a browser bundle that has no `process` even though the value was inlined.
 */
function getBasePath(): string {
  try {
    return process.env.NEXT_PUBLIC_BASE_PATH || '';
  } catch {
    return '';
  }
}

/**
 * Add base path to a route path
 */
function withBasePath(path: string, basePath: string): string {
  if (ABSOLUTE.test(path)) return path;
  if (!basePath) {
    return path;
  }
  // Ensure path starts with /
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  // Remove trailing slash from basePath
  const normalizedBasePath = basePath.replace(/\/$/, '');
  return `${normalizedBasePath}${normalizedPath}`;
}

/**
 * Router with basePath support
 *
 * Automatically adds basePath to all navigation methods when basePath is configured.
 * In Next.js 15 App Router, router.push() doesn't handle basePath automatically,
 * so this hook uses window.location to ensure basePath is always included.
 *
 * @example
 * ```tsx
 * const router = useCfgRouter();
 *
 * // With basePath='/cfg/admin':
 * router.push('/dashboard');     // Client-side navigation to '/cfg/admin/dashboard'
 * router.replace('/auth');       // Client-side replace with '/cfg/admin/auth'
 * router.hardPush('/dashboard'); // Full page reload to '/cfg/admin/dashboard'
 * router.hardReplace('/auth');   // Full page replace with '/cfg/admin/auth'
 * ```
 */
export function useCfgRouter() {
  const router = useNextRouter();

  // Get basePath
  const basePath = useMemo(() => getBasePath(), []);

  const push = useCallback((href: string, options?: { scroll?: boolean } & CfgNavOptions) => {
    const hop = ssoHop(href, options);
    if (hop) {
      authTrace('nav.sso', { from: fromPath(), to: hop });
      window.location.assign(hop);
      return;
    }
    authTrace('nav.push', { from: fromPath(), to: href });
    if (basePath) {
      // App Router doesn't handle basePath automatically, use window.location
      window.location.href = withBasePath(href, basePath);
    } else {
      // No basePath configured, use standard router
      router.push(href, options?.scroll === undefined ? undefined : { scroll: options.scroll });
    }
  }, [router, basePath]);

  const replace = useCallback((href: string, options?: { scroll?: boolean } & CfgNavOptions) => {
    const hop = ssoHop(href, options);
    if (hop) {
      authTrace('nav.sso', { from: fromPath(), to: hop });
      window.location.replace(hop);
      return;
    }
    authTrace('nav.replace', { from: fromPath(), to: href });
    if (basePath) {
      // App Router doesn't handle basePath automatically, use window.location
      window.location.replace(withBasePath(href, basePath));
    } else {
      // No basePath configured, use standard router
      router.replace(href, options?.scroll === undefined ? undefined : { scroll: options.scroll });
    }
  }, [router, basePath]);

  /**
   * Hard push - always uses window.location.href for full page reload
   *
   * Use this for auth redirects where React contexts need to reinitialize.
   * Unlike push(), this ALWAYS triggers a full page reload, ensuring all
   * contexts are reinitialized with fresh state.
   *
   * @example
   * ```tsx
   * // After successful login - contexts need to reload with new auth state
   * router.hardPush('/dashboard');
   * ```
   */
  const hardPush = useCallback((rawHref: string, options?: CfgNavOptions) => {
    const href = ssoHop(rawHref, options) ?? rawHref;
    if (hardNavigating) {
      authTrace('nav.hardPush.ignored', { from: fromPath(), to: href });
      return;
    }
    hardNavigating = true;
    authTrace('nav.hardPush', { from: fromPath(), to: href });
    window.location.href = withBasePath(href, basePath);
  }, [basePath]);

  /**
   * Hard replace - always uses window.location.replace for full page reload
   *
   * Same as hardPush but replaces current history entry.
   * Use for auth redirects where you don't want back button to return to login.
   *
   * @example
   * ```tsx
   * // After logout - replace so back button doesn't go to protected page
   * router.hardReplace('/auth');
   * ```
   */
  const hardReplace = useCallback((rawHref: string, options?: CfgNavOptions) => {
    const href = ssoHop(rawHref, options) ?? rawHref;
    if (hardNavigating) {
      authTrace('nav.hardReplace.ignored', { from: fromPath(), to: href });
      return;
    }
    hardNavigating = true;
    authTrace('nav.hardReplace', { from: fromPath(), to: href });
    window.location.replace(withBasePath(href, basePath));
  }, [basePath]);

  const prefetch = useCallback((href: string) => {
    // Prefetch doesn't need basePath handling, Next.js handles it
    router.prefetch(href);
  }, [router]);

  const back = useCallback(() => {
    router.back();
  }, [router]);

  const forward = useCallback(() => {
    router.forward();
  }, [router]);

  const refresh = useCallback(() => {
    router.refresh();
  }, [router]);

  return {
    push,
    replace,
    hardPush,
    hardReplace,
    prefetch,
    back,
    forward,
    refresh,
  };
}


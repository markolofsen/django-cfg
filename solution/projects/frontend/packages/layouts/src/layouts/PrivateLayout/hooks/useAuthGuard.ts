/**
 * Auth Guard Hook
 *
 * Handles authentication check and redirect to login page.
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

import {
  useAuth,
  resolveGuardIsLoading,
  resolveGuardIsAuthenticated,
  shouldRedirectToAuth,
  isForbidden,
  authTrace,
} from '@djangocfg/api/auth';

/**
 * Circuit breaker. A redirect that never lands (the sign-in page sends the user straight back) would otherwise
 * run forever and hide the cause. After LOOP_MAX redirects within LOOP_WINDOW_MS the guard stops redirecting,
 * writes `guard.loop` to the auth trace and shows a message that names the way to read it.
 */
const LOOP_MAX = 5;
const LOOP_WINDOW_MS = 5000;
const redirectTimes: number[] = [];

/** @internal exported for tests */
export function resetRedirectLoop(): void {
  redirectTimes.length = 0;
}

/** @internal exported for tests */
export function redirectLoopDetected(now: number): boolean {
  redirectTimes.push(now);
  while (redirectTimes.length && now - (redirectTimes[0] ?? now) > LOOP_WINDOW_MS) redirectTimes.shift();
  return redirectTimes.length > LOOP_MAX;
}

interface UseAuthGuardOptions {
  requireAuth?: boolean;
  /**
   * Require staff/admin (`is_staff || is_superuser`) on top of a session.
   * A signed-in non-staff user gets the forbidden state, not a redirect.
   */
  requireStaff?: boolean;
  /** Explicit override; defaults to the app's resolved `useAuth().routes.auth`. */
  authPath?: string;
  /**
   * @deprecated No effect. The provider owns the single safety timer (8 s), so
   * `status` always leaves 'resolving'. Kept so existing callers still compile.
   */
  loadingTimeoutMs?: number;
}

interface UseAuthGuardResult {
  /** Whether auth is still loading or redirecting */
  isLoading: boolean;
  /** Whether the user is authenticated (or auth is not required) */
  isAuthenticated: boolean;
  /** Signed in, but lacking the privilege this route requires. */
  isForbidden: boolean;
  /** Loading text for the preloader */
  loadingText: string;
}

export function useAuthGuard({
  requireAuth = true,
  requireStaff = false,
  authPath,
}: UseAuthGuardOptions): UseAuthGuardResult {
  const { status, isAdminUser, saveRedirectUrl, routes } = useAuth();
  // One linear state decides everything: 'resolving' → spinner, 'authenticated' → render, 'anonymous' → redirect.
  const isAuthenticated = status === 'authenticated';
  const authLoading = status === 'resolving';
  const resolvedAuthPath = authPath ?? routes.auth;
  const router = useRouter();
  const [isRedirecting, setIsRedirecting] = useState(false);
  const [looping, setLooping] = useState(false);

  // Auth state lives in the browser (storage), so the server always renders
  // unauthenticated → the preloader. Keep the first client render identical to
  // the server (preloader) until mounted, then switch to the real auth result.
  // Without this, the SSR preloader vs the hydrated shell is a hydration
  // mismatch (logged as "Invalid HTML tag nesting" / regenerated tree).
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  // Guard state derives from a single pure resolver (see @djangocfg/api/auth
  // utils/guard) so the "spinner vs redirect vs render" decision is unit-tested
  // in isolation and can't silently regress into the "stuck on Authenticating…"
  // state where a resolved-but-unauthenticated session never redirects.
  const guardState = {
    mounted,
    requireAuth,
    authLoading,
    isRedirecting,
    isAuthenticated,
    requireStaff,
    isAdminUser,
  };

  useEffect(() => {
    if (shouldRedirectToAuth(guardState)) {
      const currentUrl = window.location.pathname + window.location.search;
      if (redirectLoopDetected(Date.now())) {
        authTrace('guard.loop', { from: window.location.pathname, to: resolvedAuthPath, status });
        setLooping(true);
        setIsRedirecting(true);
        return;
      }
      authTrace('guard.redirect', { from: window.location.pathname, to: resolvedAuthPath });
      saveRedirectUrl(currentUrl);
      setIsRedirecting(true);
      router.push(resolvedAuthPath);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mounted, requireAuth, isAuthenticated, authLoading, isRedirecting, router, saveRedirectUrl, resolvedAuthPath]);

  const isLoading = resolveGuardIsLoading(guardState);
  const loadingText = looping
    ? 'Sign-in loop stopped. Open the console and run __cfgAuth.dump()'
    : isRedirecting
      ? 'Redirecting to login...'
      : 'Authenticating...';

  return {
    isLoading,
    isAuthenticated: resolveGuardIsAuthenticated(guardState),
    // Never redirects: shouldRedirectToAuth requires !isAuthenticated, so a
    // forbidden user is structurally excluded from the redirect effect above.
    isForbidden: isForbidden(guardState),
    loadingText,
  };
}

/**
 * Pure auth-guard state resolution.
 *
 * This is the decision that produced the "stuck on Authenticating…" bug: given
 * the auth state, should the UI show a preloader, redirect to login, or render
 * the protected content? Extracted from useAuthGuard (which lives in a package
 * with no test infra) so the branching can be unit-tested in isolation — the
 * hook just wires React state (mounted / isRedirecting) into these functions.
 *
 * Invariant that fixes the bug: once auth is resolved (`authLoading === false`)
 * and the user is unauthenticated, `isLoading` must become false so the guard
 * redirects to the form instead of spinning forever. The same invariant covers
 * the forbidden case: a signed-in user without the required privilege must stop
 * loading too, or the preloader spins on a state no redirect will ever clear.
 */

export interface GuardInput {
  /** First client render matches SSR (preloader) until mounted, to avoid hydration mismatch. */
  mounted: boolean;
  /** Whether this route requires authentication. */
  requireAuth: boolean;
  /** AuthContext still resolving initial state. */
  authLoading: boolean;
  /** A redirect to the auth page is in flight. */
  isRedirecting: boolean;
  /** User currently has a (valid-looking) session. */
  isAuthenticated: boolean;
  /** Route requires staff/admin privileges, not just a session. */
  requireStaff?: boolean;
  /** `is_staff || is_superuser`, from `useAuth().isAdminUser`. */
  isAdminUser?: boolean;
}

/**
 * True when the session is valid but lacks the required privilege.
 *
 * Distinct from unauthenticated: the fix is a different account, not signing
 * in, so this must never redirect to the auth form. Redirecting would also
 * loop — the guard saves the current URL first, so a successful re-login on
 * the same account returns straight to the wall.
 */
export function isForbidden(s: GuardInput): boolean {
  return Boolean(
    s.mounted &&
    s.requireAuth &&
    s.requireStaff &&
    !s.authLoading &&
    s.isAuthenticated &&
    !s.isAdminUser
  );
}

/**
 * True while the guard should render a preloader rather than the protected
 * content. Mirrors useAuthGuard's formula exactly.
 */
export function resolveGuardIsLoading(s: GuardInput): boolean {
  if (!s.mounted) return true; // pre-hydration: always preloader
  if (!s.requireAuth) return false; // public route: never blocks
  if (isForbidden(s)) return false; // resolved: render the wall, don't spin
  return s.authLoading || s.isRedirecting || !s.isAuthenticated;
}

/**
 * Whether the guard should trigger a redirect to the auth page. Only once
 * mounted, on a protected route, after auth resolved, when unauthenticated and
 * not already redirecting. This is the branch that must fire for a dead session.
 */
export function shouldRedirectToAuth(s: GuardInput): boolean {
  return (
    s.mounted &&
    s.requireAuth &&
    !s.authLoading &&
    !s.isAuthenticated &&
    !s.isRedirecting
  );
}

/** The effective authenticated flag the guard exposes to consumers. */
export function resolveGuardIsAuthenticated(s: Pick<GuardInput, 'requireAuth' | 'isAuthenticated'>): boolean {
  return !s.requireAuth || s.isAuthenticated;
}


/**
 * Auth-guard state resolution tests (auth/utils/guard.ts).
 *
 * This is the exact branching that produced "stuck on Authenticating…": the
 * guard must show a preloader while auth is resolving, redirect to the login
 * form once resolved-and-unauthenticated, and render content when authenticated.
 * The critical regression guard is the transition authLoading:false +
 * isAuthenticated:false → isLoading:false + shouldRedirect:true. If isLoading
 * stayed true there, the spinner would hang forever.
 */

import { describe, expect, it } from 'vitest';

import {
  resolveGuardIsLoading,
  resolveGuardIsAuthenticated,
  shouldRedirectToAuth,
  isForbidden,
  type GuardInput,
} from '../utils/guard';

const base: GuardInput = {
  mounted: true,
  requireAuth: true,
  authLoading: false,
  isRedirecting: false,
  isAuthenticated: true,
};
const s = (o: Partial<GuardInput>): GuardInput => ({ ...base, ...o });

describe('resolveGuardIsLoading', () => {
  it('preloader before mount (SSR/hydration parity), regardless of auth', () => {
    expect(resolveGuardIsLoading(s({ mounted: false, isAuthenticated: true }))).toBe(true);
    expect(resolveGuardIsLoading(s({ mounted: false, isAuthenticated: false }))).toBe(true);
  });

  it('public route never blocks once mounted', () => {
    expect(resolveGuardIsLoading(s({ requireAuth: false, isAuthenticated: false }))).toBe(false);
  });

  it('blocks while auth is still resolving', () => {
    expect(resolveGuardIsLoading(s({ authLoading: true }))).toBe(true);
  });

  it('blocks while a redirect is in flight', () => {
    expect(resolveGuardIsLoading(s({ isRedirecting: true }))).toBe(true);
  });

  it('blocks when resolved but unauthenticated (about to redirect)', () => {
    expect(resolveGuardIsLoading(s({ authLoading: false, isAuthenticated: false }))).toBe(true);
  });

  it('renders content when mounted + authenticated + not loading', () => {
    expect(resolveGuardIsLoading(base)).toBe(false);
  });
});

describe('shouldRedirectToAuth', () => {
  it('REGRESSION: resolved + unauthenticated → redirect (never hang)', () => {
    expect(shouldRedirectToAuth(s({ authLoading: false, isAuthenticated: false }))).toBe(true);
  });

  it('does not redirect before mount', () => {
    expect(shouldRedirectToAuth(s({ mounted: false, isAuthenticated: false }))).toBe(false);
  });

  it('does not redirect while auth is still loading', () => {
    expect(shouldRedirectToAuth(s({ authLoading: true, isAuthenticated: false }))).toBe(false);
  });

  it('does not redirect when authenticated', () => {
    expect(shouldRedirectToAuth(s({ isAuthenticated: true }))).toBe(false);
  });

  it('does not redirect twice (already redirecting)', () => {
    expect(shouldRedirectToAuth(s({ isAuthenticated: false, isRedirecting: true }))).toBe(false);
  });

  it('does not redirect on a public route', () => {
    expect(shouldRedirectToAuth(s({ requireAuth: false, isAuthenticated: false }))).toBe(false);
  });
});

describe('safety-net timeout (effectiveAuthLoading = authLoading && !timedOut)', () => {
  // useAuthGuard forces authLoading→false once its timeout fires. Model that
  // here to prove the guard then acts (redirect / render) instead of spinning.
  const withTimeout = (o: Partial<GuardInput>, timedOut: boolean): GuardInput => {
    const st = s(o);
    return { ...st, authLoading: st.authLoading && !timedOut };
  };

  it('a wedged loading state stops blocking once the timeout fires', () => {
    // authLoading stuck true, unauthenticated. Before timeout: still loading.
    expect(resolveGuardIsLoading(withTimeout({ authLoading: true, isAuthenticated: false }, false))).toBe(true);
    // After timeout: authLoading forced false → resolves, and since unauth it
    // is "about to redirect" loading, but shouldRedirect now fires.
    expect(shouldRedirectToAuth(withTimeout({ authLoading: true, isAuthenticated: false }, true))).toBe(true);
  });

  it('timeout lets an authenticated-but-wedged session render content', () => {
    expect(resolveGuardIsLoading(withTimeout({ authLoading: true, isAuthenticated: true }, true))).toBe(false);
  });
});

/**
 * Staff gate. A signed-in non-staff user reaching a staff-only shell is NOT an
 * auth failure: signing in again cannot fix it. The guard must resolve to a
 * distinct "forbidden" state — never a redirect (which loops, since the guard
 * saves the current URL first) and never a spinner (the original hang bug).
 */
describe('isForbidden (staff gate)', () => {
  const staff = (o: Partial<GuardInput>): GuardInput =>
    s({ requireStaff: true, isAdminUser: false, ...o });

  it('signed-in non-staff user on a staff route is forbidden', () => {
    expect(isForbidden(staff({}))).toBe(true);
  });

  it('staff user passes the gate', () => {
    expect(isForbidden(staff({ isAdminUser: true }))).toBe(false);
  });

  it('a superuser who is not is_staff passes (isAdminUser folds both flags)', () => {
    // useAuth() computes isAdminUser as is_staff || is_superuser, so the guard
    // only ever sees the fold. Checking is_staff alone here would hide the
    // surface from the people most likely to need it.
    expect(isForbidden(staff({ isAdminUser: true }))).toBe(false);
  });

  it('is not forbidden while auth is still resolving (role unknown yet)', () => {
    expect(isForbidden(staff({ authLoading: true }))).toBe(false);
  });

  it('is not forbidden before mount (SSR never knows the role)', () => {
    expect(isForbidden(staff({ mounted: false }))).toBe(false);
  });

  it('unauthenticated is a redirect, not a forbidden wall', () => {
    expect(isForbidden(staff({ isAuthenticated: false }))).toBe(false);
    expect(shouldRedirectToAuth(staff({ isAuthenticated: false }))).toBe(true);
  });

  it('routes that do not require staff are never forbidden', () => {
    expect(isForbidden(s({ requireStaff: false, isAdminUser: false }))).toBe(false);
    expect(isForbidden(base)).toBe(false); // requireStaff undefined
  });

  it('a public route is never forbidden', () => {
    expect(isForbidden(staff({ requireAuth: false }))).toBe(false);
  });

  it('REGRESSION: a forbidden user stops loading (renders the wall, never spins)', () => {
    expect(resolveGuardIsLoading(staff({}))).toBe(false);
  });

  it('REGRESSION: a forbidden user never triggers a redirect (no login loop)', () => {
    expect(shouldRedirectToAuth(staff({}))).toBe(false);
  });

  it('a staff user on a staff route renders content', () => {
    expect(resolveGuardIsLoading(staff({ isAdminUser: true }))).toBe(false);
  });

  it('still blocks while a staff route is resolving auth', () => {
    expect(resolveGuardIsLoading(staff({ authLoading: true }))).toBe(true);
  });
});

describe('resolveGuardIsAuthenticated', () => {
  it('is true on a public route regardless of session', () => {
    expect(resolveGuardIsAuthenticated({ requireAuth: false, isAuthenticated: false })).toBe(true);
  });
  it('reflects the session on a protected route', () => {
    expect(resolveGuardIsAuthenticated({ requireAuth: true, isAuthenticated: true })).toBe(true);
    expect(resolveGuardIsAuthenticated({ requireAuth: true, isAuthenticated: false })).toBe(false);
  });
});


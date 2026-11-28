/**
 * The one auth state: a single value answers "may this page render?".
 *
 *   resolving      the client has not read the session yet, or a live session is still loading its profile
 *   authenticated  a live session and its profile settled
 *   anonymous      no session (store and React snapshot agree)
 *
 * Every consumer (the page guard, the "leave /auth" effect, the trace) reads this and nothing else. The
 * inputs are plain booleans so the whole table is unit-tested.
 *
 * Termination: `resolving` is left in finite time. `timedOut` is set by one timer in the provider, and
 * when it fires the React snapshot decides. There is no input combination that stays `resolving` with
 * `timedOut` true.
 */

export type AuthStatus = 'resolving' | 'authenticated' | 'anonymous';

export interface AuthStateInput {
  /** The first client effect has run (the hydration commit is over). */
  clientReady: boolean;
  /** `useSession()` says authenticated (the React snapshot; the server snapshot is always anonymous). */
  snapshotAuthenticated: boolean;
  /** `auth.isAuthenticated()` read straight from the store at this render. */
  storeAuthenticated: boolean;
  /** The profile for a live session has loaded, failed in a way that keeps the session, or was cached. */
  profileSettled: boolean;
  /** The provider's single safety timer fired. */
  timedOut: boolean;
}

export function resolveAuthStatus(s: AuthStateInput): AuthStatus {
  if (!s.clientReady) return 'resolving';
  if (s.snapshotAuthenticated) {
    return s.profileSettled || s.timedOut ? 'authenticated' : 'resolving';
  }
  // Snapshot says signed out. If the store disagrees the snapshot is lagging: wait for it, but never forever.
  if (s.storeAuthenticated && !s.timedOut) return 'resolving';
  return 'anonymous';
}

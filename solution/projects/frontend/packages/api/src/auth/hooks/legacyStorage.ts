/**
 * One-time cleanup of what the pre-cookie auth left in the browser.
 *
 * Before 2.1.604 the session tokens lived in `localStorage`. They are cookies now (shared across subdomains), so the old
 * entries are never read again; left alone they are harmless but misleading, and the 4 h profile cache next to them used
 * to keep the UI looking signed in without any token (empty private pages). Cookies are untouched.
 */

const LEGACY_TOKEN_KEYS = [
  'cfg.auth.access_token',
  'cfg.auth.refresh_token',
  'auth_token',
  'refresh_token',
  'access_token',
] as const;

/** Removes the old `localStorage` token entries. Safe on the server and with blocked storage. */
export function purgeLegacyTokenStorage(): string[] {
  const removed: string[] = [];
  try {
    if (typeof window === 'undefined') return removed;
    for (const key of LEGACY_TOKEN_KEYS) {
      if (window.localStorage.getItem(key) !== null) {
        window.localStorage.removeItem(key);
        removed.push(key);
      }
    }
  } catch {
    /* storage blocked: nothing to purge */
  }
  return removed;
}

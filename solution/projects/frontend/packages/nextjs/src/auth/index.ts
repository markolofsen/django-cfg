/**
 * Server-side view of the shared session cookie.
 *
 * `@djangocfg/api` keeps the JWT pair in cookies on the registrable domain, so a Server
 * Component, route handler or `generateMetadata` on any subdomain sees the same session
 * with no setup:
 *
 * ```ts
 * import { serverAuthHeaders } from '@djangocfg/nextjs/auth';
 * const res = await fetch(`${API}/cfg/accounts/profile/`, { headers: await serverAuthHeaders() });
 * ```
 *
 * The API authenticates the `Authorization` header only; this cookie is never an
 * authenticator by itself, so reading it here creates no CSRF surface.
 */
import { cookies } from 'next/headers';
import { CFG_KEYS } from '@djangocfg/api/storage';

async function readSessionCookie(name: string): Promise<string | null> {
  try {
    const raw = (await cookies()).get(name)?.value;
    return raw ? decodeURIComponent(raw) : null;
  } catch {
    // Outside a request scope (build time, static generation): no session.
    return null;
  }
}

/** The access token of the signed-in user, or `null`. May be expired: the API decides. */
export function getServerAccessToken(): Promise<string | null> {
  return readSessionCookie(CFG_KEYS.accessToken.key);
}

/** The refresh token, or `null`. Rarely needed on the server. */
export function getServerRefreshToken(): Promise<string | null> {
  return readSessionCookie(CFG_KEYS.refreshToken.key);
}

/** `{ Authorization: 'Bearer …' }` for a server-side fetch; `{}` when signed out. */
export async function serverAuthHeaders(): Promise<Record<string, string>> {
  const token = await getServerAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

/** Whether a session cookie is present (not whether it is still valid). */
export async function hasServerSession(): Promise<boolean> {
  return (await getServerAccessToken()) !== null || (await getServerRefreshToken()) !== null;
}

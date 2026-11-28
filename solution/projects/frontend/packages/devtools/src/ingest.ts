/**
 * Ingest transport — one plain fetch to `POST /cfg/monitor/ingest/`.
 *
 * The endpoint is AllowAny + rate-limited on the backend and always answers
 * 202; nothing here needs a generated client. When the visitor is signed in, the
 * regular send adds `Authorization: Bearer <access token>` (see `readAccessToken`)
 * so the server can log the user's id next to the error; with no token the
 * request is exactly what it was, and an invalid token is ignored server-side.
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * WHY THIS DOES NOT USE @djangocfg/analytics' BeaconTransport
 * ─────────────────────────────────────────────────────────────────────────────
 * It would be the obvious dedup, and it is wrong: BeaconTransport is
 * fire-and-forget, while `sendBatch` MUST reject on failure — `store.ts` drives
 * a circuit breaker off that rejection (BREAKER_THRESHOLD / BREAKER_COOLDOWN_MS),
 * and `server.ts` awaits it outside the browser entirely. Swapping in a
 * fire-and-forget transport would silently disable the breaker, so a backend
 * outage would turn into an unbounded retry loop from every open tab.
 *
 * What IS shared is the rule below, and it is the part that was actually broken.
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * THE UNLOAD PATH MUST NOT SEND application/json
 * ─────────────────────────────────────────────────────────────────────────────
 * `application/json` is NOT CORS-safelisted, so a cross-origin request carrying
 * it leaves no-cors mode and triggers an OPTIONS preflight. During page unload
 * that preflight usually cannot complete, so the POST is never sent — and the
 * events lost are the ones that mattered most: whatever crashed the page and
 * caused the navigation away.
 *
 * `text/plain` IS CORS-safelisted, so the same JSON body is delivered with no
 * preflight. The body is unchanged; only the label differs. The server reads it
 * with an additive parser scoped to the ingest view.
 *
 * Same trap, same fix, as @djangocfg/analytics. Verified in Chrome 149.
 */

import { CFG_KEYS, cfgStorage } from '@djangocfg/api/storage'

import { INGEST_PATH } from './internal'
import type { DevtoolsEvent } from './types'

/**
 * The access token the `@djangocfg/api` client sends, or null.
 *
 * Read from the same registry key (`cfg.auth.access_token`) in the order the client
 * can have stored it: the shared cookie (default), then localStorage, then
 * sessionStorage (hosts that called `setStorageMode`). Browser only; the Node
 * `server` entry has no token and sends none.
 */
export function readAccessToken(): string | null {
  if (typeof window === 'undefined') return null
  for (const store of ['cookie', 'local', 'session'] as const) {
    try {
      const value = cfgStorage.read(CFG_KEYS.accessToken.key, store)
      if (value) return value
    } catch {
      /* storage blocked: try the next one */
    }
  }
  return null
}

export async function sendBatch(
  baseUrl: string,
  events: DevtoolsEvent[],
  useBeacon = false,
): Promise<void> {
  if (events.length === 0) return

  // No API origin configured → drop the batch instead of posting to a relative
  // path. A relative URL resolves against the CURRENT page, so on an
  // i18n-prefixed route this would POST to `/<locale>/cfg/monitor/ingest/` on
  // the site's own origin: a guaranteed 404, and — because a failed send trips
  // the circuit breaker in `store.ts` — a retry loop from every open tab.
  // Returning cleanly keeps the breaker closed and the app silent.
  if (!baseUrl) return

  const headers: Record<string, string> = {
    // Unload flushes must stay CORS-simple or they never leave the browser.
    'Content-Type': useBeacon ? 'text/plain' : 'application/json',
  }
  // `Authorization` is not CORS-safelisted either: on the unload flush it would bring
  // the preflight back and lose the very event that mattered. So the unload flush is
  // sent anonymous; every regular flush (5 s timer, buffer full, ping) carries the user.
  if (!useBeacon) {
    const token = readAccessToken()
    if (token) headers.Authorization = `Bearer ${token}`
  }

  const res = await fetch(`${baseUrl}${INGEST_PATH}`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ events }),
    credentials: 'include',
    ...(useBeacon ? { keepalive: true } : {}),
  })
  if (!res.ok) throw new Error(`ingest ${res.status}`)
}

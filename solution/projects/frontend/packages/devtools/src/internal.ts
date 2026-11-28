import { CFG_KEYS } from '@djangocfg/api/storage'
/**
 * Internal utilities: environment, session identity, fingerprinting, dedupe.
 */

// ─── Environment ─────────────────────────────────────────────────────────────

/** True only in next dev / jest / vitest */
export const isDevelopment = process.env.NODE_ENV === 'development'

/** True in any non-development environment */
export const isProduction = !isDevelopment

/** Ingest endpoint (django_monitor extension). */
export const INGEST_PATH = '/cfg/monitor/ingest/'

/** Matches requests to the ingest endpoint — prevents capture→flush feedback loops. */
export const INGEST_PATTERN = /cfg\/monitor\/ingest/

export const DEFAULT_DEDUPE_TTL = 30_000
export const DEFAULT_FLUSH_INTERVAL = 5_000
export const DEFAULT_MAX_BUFFER = 20

// ─── Session identity ────────────────────────────────────────────────────────

const SESSION_KEY = CFG_KEYS.monitorSessionId.key
const COOKIE_MAX_AGE = 60 * 60 * 24 * 365

function generateUUID(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID()
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16)
  })
}

export function getSessionId(): string {
  if (typeof localStorage === 'undefined') return ''
  try {
    let id = localStorage.getItem(SESSION_KEY)
    if (!id) {
      id = generateUUID()
      localStorage.setItem(SESSION_KEY, id)
      document.cookie = `${SESSION_KEY}=${id}; path=/; SameSite=Lax; max-age=${COOKIE_MAX_AGE}`
    }
    return id
  } catch {
    return ''
  }
}

// ─── Fingerprint (sync — no crypto.subtle round-trip needed for dedup) ──────

export function computeFingerprint(message: string, stack: string, url: string): string {
  const raw = `${message}|${stack}|${url}`
  let hash = 0
  for (let i = 0; i < raw.length; i++) {
    hash = (hash << 5) - hash + raw.charCodeAt(i)
    hash = hash & hash
  }
  return Math.abs(hash).toString(16).padStart(8, '0')
}

// ─── Dedupe ──────────────────────────────────────────────────────────────────

/** TTL-based seen-set with a size cap. One instance guards one capture path. */
export function makeDeduper(max = 200): (key: string, ttl: number) => boolean {
  const seen = new Map<string, number>()
  return (key, ttl) => {
    const now = Date.now()
    const last = seen.get(key)
    if (last !== undefined && now - last < ttl) return true
    seen.set(key, now)
    if (seen.size > max) {
      for (const [k, ts] of seen) {
        if (now - ts > ttl) seen.delete(k)
      }
    }
    return false
  }
}

export function truncate(s: string, max: number): string {
  return s.length > max ? s.slice(0, max - 1) + '…' : s
}

/**
 * The console as it was before `installConsoleCapture` wrapped it.
 *
 * Bound at module load, which runs before any install, so callers that must
 * NOT feed capture — the local logger — can still print. Going through the
 * wrapped console instead turns a panel-only log line into an ingested event.
 */
export const rawConsole = {
  log: console.log.bind(console),
  warn: console.warn.bind(console),
  error: console.error.bind(console),
}

/**
 * @djangocfg/devtools — shared types.
 *
 * `DevtoolsEvent` is the hand-written contract of `POST /cfg/monitor/ingest/`
 * (django-cfg's django_monitor extension). The endpoint is a stable, additive
 * API — a generated OpenAPI client here would be 2k+ lines to describe one
 * POST, so we don't. If the backend contract changes shape (it shouldn't),
 * this file is the single place to update.
 */

// ─── Backend event contract ──────────────────────────────────────────────────

export const EventType = {
  JS_ERROR: 'JS_ERROR',
  NETWORK_ERROR: 'NETWORK_ERROR',
  ERROR: 'ERROR',
  WARNING: 'WARNING',
  CONSOLE: 'CONSOLE',
} as const
export type EventType = (typeof EventType)[keyof typeof EventType]

export const EventLevel = {
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
  DEBUG: 'debug',
} as const
export type EventLevel = (typeof EventLevel)[keyof typeof EventLevel]

/** One ingest event. Field limits mirror the backend serializer. */
export interface DevtoolsEvent {
  event_type: EventType
  message: string
  level?: EventLevel
  stack_trace?: string
  url?: string
  fingerprint?: string
  http_status?: number | null
  http_method?: string
  http_url?: string
  session_id?: string
  user_agent?: string
  build_id?: string
  environment?: string
  extra?: unknown
  project_name?: string
}

// ─── Config ──────────────────────────────────────────────────────────────────

export interface DevtoolsConfig {
  /**
   * Base URL for the django-cfg backend. Default: NEXT_PUBLIC_API_URL. With no value
   * at all ingest cannot send: devtools warns once in the console and
   * `devtools.status()` shows `baseUrl: ''`. BaseApp fills it from `auth.apiUrl`.
   */
  baseUrl?: string
  /** Project name sent with every event */
  project?: string
  /** Environment tag: production / staging / development */
  environment?: string
  /** Next.js BUILD_ID for server-side source map deminification */
  buildId?: string
  /** Send captured errors/warnings to the backend ingest endpoint. Default: true */
  ingest?: boolean
  /** Capture window.onerror + unhandledrejection. Default: true */
  captureJsErrors?: boolean
  /** Capture console.warn / console.error. Default: true */
  captureConsole?: boolean
  /** Ingest flush interval in ms. Default: 5000 */
  flushInterval?: number
  /** Max events in the outbox before immediate flush. Default: 20 */
  maxBufferSize?: number
  /** Deduplication TTL in ms (same event captured twice). Default: 30000 */
  dedupeTtl?: number
  /** Log devtools internals to console. Default: false */
  debug?: boolean
}

/** What `devtools.status()` returns: the state of the ingest pipe. */
export interface DevtoolsStatus {
  /** Ingest is enabled (`ingest !== false`) */
  ingest: boolean
  /** Resolved API origin; empty means events are dropped */
  baseUrl: string
  /** Events waiting in the outbox */
  queued: number
  /** Events the backend accepted (2xx) */
  sent: number
  /** Events that failed to send or were dropped */
  failed: number
  lastError: string | null
  /** ms epoch of the last successful send */
  lastSentAt: number | null
  /** Ingest paused by the circuit breaker after repeated failures */
  circuitOpen: boolean
}

export interface ServerDevtoolsConfig {
  /** Base URL for the django-cfg backend (absolute URL required on server) */
  baseUrl?: string
  project?: string
  environment?: string
}

// ─── Panel log entries (local, never sent anywhere) ─────────────────────────

export type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'success'

export interface LogEntry {
  id: string
  timestamp: Date
  level: LogLevel
  /** Where the entry came from: a component name, or `capture:<event_type>` */
  source: string
  message: string
  data?: Record<string, unknown>
  stack?: string
}

export interface Logger {
  debug: (message: string, data?: Record<string, unknown>) => void
  info: (message: string, data?: Record<string, unknown>) => void
  warn: (message: string, data?: Record<string, unknown>) => void
  error: (message: string, data?: Record<string, unknown>) => void
  success: (message: string, data?: Record<string, unknown>) => void
}

// ─── Panel customization ─────────────────────────────────────────────────────

export interface CustomDebugTab {
  id: string
  label: string
  icon: React.ElementType
  panel: React.ComponentType<{ isActive: boolean }>
}

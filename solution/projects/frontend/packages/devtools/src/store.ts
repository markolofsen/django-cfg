/**
 * The ONE devtools store.
 *
 * Everything flows through here: captured events land in `entries` (what the
 * panel renders) and — when ingest-worthy — in `outbox` (what gets POSTed to
 * the backend). The old monitor/debuger split kept two stores synced through
 * a bridge; a single store makes that whole layer unnecessary.
 *
 * Vanilla store so it works outside React (capture hooks, console API);
 * React components subscribe via `useStore` from zustand.
 */

import { createStore } from 'zustand/vanilla'

import { sendBatch } from './ingest'
import {
  DEFAULT_DEDUPE_TTL,
  DEFAULT_MAX_BUFFER,
  computeFingerprint,
  makeDeduper,
  truncate,
} from './internal'
import type { DevtoolsConfig, DevtoolsEvent, LogEntry, LogLevel } from './types'

const MAX_ENTRIES = 1000
const MAX_BATCH = 25
// Ceiling for events held while ingest is failing. The oldest are dropped
// first: during an outage the newest events describe the current state.
const MAX_OUTBOX = 200

// Circuit breaker: pause ingest after N consecutive transport failures
const BREAKER_THRESHOLD = 3
const BREAKER_COOLDOWN_MS = 60_000

const isRecent = makeDeduper()

let _counter = 0
const nextId = () => `dt-${Date.now()}-${++_counter}`

const eventToLogLevel: Record<string, LogLevel> = {
  error: 'error',
  warning: 'warn',
  info: 'info',
  debug: 'debug',
}

export interface DevtoolsState {
  config: DevtoolsConfig
  /** Panel feed — every captured event and local log line (ring buffer). */
  entries: LogEntry[]
  /** Events waiting to be POSTed to the ingest endpoint. */
  outbox: DevtoolsEvent[]
  // Panel UI
  isOpen: boolean
  tab: string
  // Circuit breaker
  _failures: number
  _pausedUntil: number
  // Ingest counters, read by `devtools.status()`
  _sent: number
  _failed: number
  _lastError: string | null
  _lastSentAt: number | null

  setConfig: (config: DevtoolsConfig) => void
  /** Add a local panel entry (loggers, custom instrumentation). Never ingested. */
  addEntry: (entry: Omit<LogEntry, 'id' | 'timestamp'>) => void
  /** Capture an event: panel entry + (if enabled) ingest outbox. */
  capture: (event: DevtoolsEvent) => void
  /** Send the outbox now. Resolves when the batch was delivered or failed. */
  flush: (useBeacon?: boolean) => Promise<void>
  clearEntries: () => void
  // Panel UI
  openPanel: () => void
  closePanel: () => void
  togglePanel: () => void
  setTab: (tab: string) => void
}

export const devtoolsStore = createStore<DevtoolsState>((set, get) => ({
  config: {},
  entries: [],
  outbox: [],
  isOpen: false,
  tab: 'logs',
  _failures: 0,
  _pausedUntil: 0,
  _sent: 0,
  _failed: 0,
  _lastError: null,
  _lastSentAt: null,

  setConfig(config) {
    set({ config })
  },

  addEntry(entry) {
    const next = [...get().entries, { ...entry, id: nextId(), timestamp: new Date() }]
    set({ entries: next.length > MAX_ENTRIES ? next.slice(-MAX_ENTRIES) : next })
  },

  capture(event) {
    const { config } = get()

    const message = truncate(event.message ?? '', 4997)
    const stack = event.stack_trace ? truncate(event.stack_trace, 9997) : event.stack_trace
    const fingerprint =
      event.fingerprint ?? computeFingerprint(message, stack ?? '', event.http_url ?? event.url ?? '')

    // One dedupe for everything: same fingerprint within TTL → drop entirely.
    if (isRecent(fingerprint, config.dedupeTtl ?? DEFAULT_DEDUPE_TTL)) return

    get().addEntry({
      level: eventToLogLevel[event.level ?? 'error'] ?? 'error',
      source: `capture:${event.event_type.toLowerCase()}`,
      message,
      data: {
        ...(event.http_status != null && {
          http_status: event.http_status,
          http_method: event.http_method,
          http_url: event.http_url,
        }),
        ...(event.extra ? { extra: event.extra } : {}),
      },
      stack: stack || undefined,
    })

    if (config.ingest === false) return

    const sanitized: DevtoolsEvent = {
      ...event,
      message,
      stack_trace: stack,
      fingerprint,
      build_id: event.build_id ?? config.buildId ?? '',
      project_name: event.project_name ?? config.project,
      environment: event.environment ?? config.environment,
      // Drop oversized extras instead of failing serializer-side.
      extra: (() => {
        if (!event.extra) return event.extra
        try {
          return JSON.stringify(event.extra).length > 32_768 ? {} : event.extra
        } catch {
          return {}
        }
      })(),
    }

    const outbox = [...get().outbox, sanitized]
    set({ outbox })

    if (outbox.length >= (config.maxBufferSize ?? DEFAULT_MAX_BUFFER) || event.level === 'error') {
      void get().flush()
    }
  },

  flush(useBeacon = false) {
    const { outbox, config, _pausedUntil } = get()
    if (outbox.length === 0 || Date.now() < _pausedUntil) return Promise.resolve()

    const batch = outbox.slice(0, MAX_BATCH)
    set({ outbox: outbox.slice(MAX_BATCH) })

    // No API origin: sendBatch would drop the batch silently. Count it as
    // failed and say why, so `devtools.status()` shows the misconfiguration.
    // Not a transport failure, so the circuit breaker stays closed.
    if (!config.baseUrl) {
      set({
        _failed: get()._failed + batch.length,
        _lastError: 'no baseUrl: events dropped (pass devtools={{ baseUrl }} or set NEXT_PUBLIC_API_URL)',
      })
      return Promise.resolve()
    }

    return sendBatch(config.baseUrl, batch, useBeacon).then(
      () => set({ _failures: 0, _pausedUntil: 0, _sent: get()._sent + batch.length, _lastSentAt: Date.now() }),
      (err: unknown) => {
        const failures = get()._failures + 1
        // Put the batch back, ahead of whatever arrived meanwhile: a failed
        // send must not consume the events. Dropping them here would lose
        // exactly the reports of an incident the backend was too busy to take.
        // A beacon flush is the exception — the page is going away and there
        // is no later attempt to hand them to.
        const requeued = useBeacon ? get().outbox : [...batch, ...get().outbox]
        set({
          outbox: requeued.length > MAX_OUTBOX ? requeued.slice(-MAX_OUTBOX) : requeued,
          _failures: failures,
          _failed: get()._failed + batch.length,
          _lastError: err instanceof Error ? err.message : String(err),
          _pausedUntil:
            failures >= BREAKER_THRESHOLD ? Date.now() + BREAKER_COOLDOWN_MS : get()._pausedUntil,
        })
      },
    )
  },

  clearEntries: () => set({ entries: [] }),

  openPanel: () => set({ isOpen: true }),
  closePanel: () => set({ isOpen: false }),
  togglePanel: () => set((s) => ({ isOpen: !s.isOpen })),
  setTab: (tab) => set({ tab }),
}))

/**
 * The `devtools` singleton — the imperative API.
 *
 * React apps normally never call `init`/`destroy` directly; the `<Devtools />`
 * component does. Everything else (`capture`, `error`, `log`) is safe to call
 * from anywhere, any time — before init it just fills the panel feed.
 *
 * From the browser console the same API is available as `window.devtools`.
 */

import {
  installConsoleCapture,
  installJsErrorCapture,
  installValidationCapture,
  installNetworkCapture,
} from './capture'
import { DEFAULT_FLUSH_INTERVAL, getSessionId, isDevelopment, rawConsole } from './internal'
import { devtoolsStore } from './store'
import { EventLevel, EventType } from './types'
import type { DevtoolsConfig, DevtoolsEvent, DevtoolsStatus, Logger } from './types'

let warnedNoBaseUrl = false
let flushTimer: ReturnType<typeof setInterval> | null = null
const cleanups: Array<() => void> = []

function makeEvent(
  type: EventType,
  level: EventLevel,
  message: string,
  extra?: Record<string, unknown>,
): DevtoolsEvent {
  return {
    event_type: type,
    level,
    message,
    url: typeof window !== 'undefined' ? window.location.href : '',
    session_id: getSessionId(),
    user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
    ...(extra ? { extra } : {}),
  }
}

/** Pull an Error out of `data.error` so the panel gets a proper stack. */
function extractStack(data?: Record<string, unknown>): {
  cleanData?: Record<string, unknown>
  stack?: string
} {
  if (!data) return {}
  const cleanData = { ...data }
  let stack: string | undefined
  const err = data.error
  if (err instanceof Error) {
    stack = err.stack
    cleanData.error = { name: err.name, message: err.message }
  } else if (typeof err === 'object' && err !== null) {
    const e = err as Record<string, unknown>
    if (typeof e.stack === 'string') stack = e.stack
    if (typeof e.message === 'string') cleanData.error = e.message
  }
  return { cleanData, stack }
}

export const devtools = {
  /** Install capture hooks + start the ingest pump. Idempotent per mount. */
  init(config: DevtoolsConfig = {}): void {
    if (typeof window === 'undefined') return

    const resolved: DevtoolsConfig = {
      ...config,
      baseUrl: config.baseUrl ?? process.env.NEXT_PUBLIC_API_URL ?? '',
    }
    devtoolsStore.getState().setConfig(resolved)
    if (resolved.ingest !== false && !resolved.baseUrl && !warnedNoBaseUrl) {
      warnedNoBaseUrl = true
      // rawConsole: the wrapped console.warn would feed this line into capture.
      rawConsole.warn(
        '[devtools] ingest is on but no base URL resolved, so browser errors are NOT sent to the backend. ' +
          "Fix: pass devtools={{ baseUrl: 'https://api.example.com' }} (or BaseApp apiUrl / auth.apiUrl), " +
          'or declare NEXT_PUBLIC_API_URL at build time (turbo env is an allow-list). Check with window.devtools.status().',
      )
    }
    getSessionId() // ensure the session cookie exists

    if (resolved.captureJsErrors !== false) cleanups.push(installJsErrorCapture())
    if (resolved.captureConsole !== false) cleanups.push(installConsoleCapture())
    cleanups.push(installValidationCapture(), installNetworkCapture())

    flushTimer = setInterval(
      () => devtoolsStore.getState().flush(),
      resolved.flushInterval ?? DEFAULT_FLUSH_INTERVAL,
    )
    const onHide = () => {
      if (document.visibilityState === 'hidden') devtoolsStore.getState().flush(true)
    }
    document.addEventListener('visibilitychange', onHide)
    cleanups.push(() => document.removeEventListener('visibilitychange', onHide))

    window.devtools = devtools

    if (resolved.debug) console.info('[devtools] initialized', resolved)
  },

  destroy(): void {
    if (flushTimer !== null) {
      clearInterval(flushTimer)
      flushTimer = null
    }
    cleanups.forEach((fn) => fn())
    cleanups.length = 0
  },

  /** Capture a raw event (panel + backend ingest). */
  capture(event: DevtoolsEvent): void {
    devtoolsStore.getState().capture(event)
  },

  error(message: string, extra?: Record<string, unknown>): void {
    devtoolsStore.getState().capture(makeEvent(EventType.JS_ERROR, EventLevel.ERROR, message, extra))
  },

  warn(message: string, extra?: Record<string, unknown>): void {
    devtoolsStore.getState().capture(makeEvent(EventType.WARNING, EventLevel.WARNING, message, extra))
  },

  info(message: string, extra?: Record<string, unknown>): void {
    devtoolsStore.getState().capture(makeEvent(EventType.WARNING, EventLevel.INFO, message, extra))
  },

  network(status: number, method: string, url: string, extra?: Record<string, unknown>): void {
    devtoolsStore.getState().capture({
      ...makeEvent(
        EventType.NETWORK_ERROR,
        status >= 500 ? EventLevel.ERROR : EventLevel.WARNING,
        `${method} ${url} → ${status}`,
        extra,
      ),
      http_status: status,
      http_method: method,
      http_url: url,
    })
  },

  /**
   * Component-scoped local logger. Entries go to the debug panel (and the
   * console in dev) — never to the backend. For "send this to the backend",
   * use `capture`/`error` instead.
   */
  log(source: string): Logger {
    const write = (
      level: 'debug' | 'info' | 'warn' | 'error' | 'success',
      message: string,
      data?: Record<string, unknown>,
    ) => {
      const { cleanData, stack } = extractStack(data)
      if (typeof window !== 'undefined') {
        devtoolsStore.getState().addEntry({ level, source, message, data: cleanData, stack })
      }
      if (isDevelopment) {
        // rawConsole, not console: `installConsoleCapture` wraps console.error
        // and console.warn, so printing through them would feed this
        // panel-only line back into capture and ingest it.
        const method = level === 'error' ? 'error' : level === 'warn' ? 'warn' : 'log'
        if (cleanData) rawConsole[method](`[${source}]`, message, cleanData)
        else rawConsole[method](`[${source}]`, message)
      }
    }
    return {
      debug: (msg, data) => write('debug', msg, data),
      info: (msg, data) => write('info', msg, data),
      warn: (msg, data) => write('warn', msg, data),
      error: (msg, data) => write('error', msg, data),
      success: (msg, data) => write('success', msg, data),
    }
  },

  /** Force-flush the ingest outbox. */
  flush(): void {
    void devtoolsStore.getState().flush()
  },

  /**
   * State of the ingest pipe, also printed to the console. Returns
   * {ingest, baseUrl, queued, sent, failed, lastError, lastSentAt, circuitOpen}.
   */
  status(): DevtoolsStatus {
    const s = devtoolsStore.getState()
    const result: DevtoolsStatus = {
      ingest: s.config.ingest !== false,
      baseUrl: s.config.baseUrl ?? '',
      queued: s.outbox.length,
      sent: s._sent,
      failed: s._failed,
      lastError: s._lastError,
      lastSentAt: s._lastSentAt,
      circuitOpen: Date.now() < s._pausedUntil,
    }
    console.group('[devtools] status')
    console.log('ingest:', result)
    console.log('config:', s.config)
    console.log('panel entries:', s.entries.length)
    console.log('session_id:', getSessionId())
    console.groupEnd()
    return result
  },

  /**
   * End-to-end check: sends one info-level `devtools ping` event to the backend
   * now (django_monitor logs it, never alerts) and resolves with `status()`.
   * Then `manage.py monitor_tail --frontend` shows it on the server.
   */
  async ping(): Promise<DevtoolsStatus> {
    const s = devtoolsStore.getState()
    const event = makeEvent(EventType.WARNING, EventLevel.INFO, 'devtools ping', { ping: true })
    // A unique fingerprint: the dedupe would drop a second ping within 30 s.
    s.capture({ ...event, fingerprint: `devtools-ping-${Date.now()}` })
    await devtoolsStore.getState().flush()
    return devtools.status()
  },
}

export type DevtoolsApi = typeof devtools

declare global {
  interface Window {
    devtools?: DevtoolsApi
  }
}

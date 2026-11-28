/**
 * Browser capture hooks. Each installer returns its cleanup function.
 * Everything funnels into `devtoolsStore.capture()` — dedupe, panel entry,
 * and ingest buffering all happen there, once.
 */

import { devtoolsStore } from './store'
import { INGEST_PATTERN, getSessionId, truncate } from './internal'
import { EventLevel, EventType } from './types'
import type { DevtoolsEvent } from './types'

const MSG_MAX = 2000
const ARG_MAX = 500

// Hydration mismatches caused by browser extensions (Grammarly, translators…).
// Not application bugs — filtering them prevents alert noise.
const HYDRATION_NOISE: RegExp[] = [
  /hydration failed/i,
  /there was an error while hydrating/i,
  /minified react error #418/i,
  /minified react error #423/i,
  /minified react error #425/i,
  /text content does not match server-rendered html/i,
]

// Third-party libraries that log a handled failure through console.error.
// The call already succeeded or fell back, so reporting it alerts on nothing.
const LIBRARY_NOISE: RegExp[] = [
  // input-otp probes `:autofill`, which older engines reject, then installs
  // the `-webkit-autofill` rule that actually applies. Nothing is broken.
  /input-otp could not insert CSS rule/i,
]

// React's streaming-SSR runtime: the inline `$RS` (reveal segment), `$RC`
// (complete boundary) and kin that the server writes into the HTML to move
// each late chunk from its `<div hidden id="S:n">` into its placeholder.
// They throw only when that hidden element is already gone — something
// outside the app rewrote the document before the stream finished (a
// headless scraper stripping hidden nodes, a reader-mode or translation
// rewrite). The frame is React's, never the app's, and nothing on the page
// can fix it. Measured on carapis.com, 2026-09-23: 19,381 events in a day,
// 99.9% from one fixed "Chrome/145" user agent, each page load failing all
// 19 of its `$RS` calls at once — while a real browser on the same URL
// raised none.
const STREAMING_RUNTIME_FRAME = /^\s*at \$R[A-Z]{1,2} \(/m

export function isStreamingRuntimeNoise(stack?: string): boolean {
  if (!stack) return false
  // The TOP frame only: an app error that merely passed through a streamed
  // chunk still has its own frame first, and must still be reported.
  const firstFrame = stack.split('\n').find((line) => /^\s*at /.test(line))
  return firstFrame !== undefined && STREAMING_RUNTIME_FRAME.test(firstFrame)
}

function isNoise(msg: string, stack?: string): boolean {
  if (HYDRATION_NOISE.some((p) => p.test(msg))) return true
  if (LIBRARY_NOISE.some((p) => p.test(msg))) return true
  if (isStreamingRuntimeNoise(stack)) return true
  // Our own transport failing must never loop back into capture.
  return INGEST_PATTERN.test(msg) || INGEST_PATTERN.test(stack ?? '')
}

function browserContext(): Pick<DevtoolsEvent, 'url' | 'session_id' | 'user_agent'> {
  return {
    url: typeof window !== 'undefined' ? window.location.href : '',
    session_id: getSessionId(),
    user_agent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
  }
}

// ─── window.onerror + unhandledrejection ────────────────────────────────────

export function installJsErrorCapture(): () => void {
  if (typeof window === 'undefined') return () => {}

  const report = (msg: string, stack: string) => {
    try {
      if (isNoise(msg, stack)) return
      devtoolsStore.getState().capture({
        event_type: EventType.JS_ERROR,
        level: EventLevel.ERROR,
        message: truncate(msg, MSG_MAX),
        stack_trace: stack,
        ...browserContext(),
      })
    } catch {
      /* never crash the host app */
    }
  }

  const onError = (e: ErrorEvent) => {
    const msg = e.message || String(e.error ?? 'Unknown error')
    report(msg, e.error?.stack ?? `at ${e.filename}:${e.lineno}:${e.colno}`)
  }

  const onRejection = (e: PromiseRejectionEvent) => {
    const reason = e.reason
    const msg =
      reason instanceof Error
        ? reason.message
        : typeof reason === 'string'
          ? reason
          : 'Unhandled promise rejection'
    report(msg, reason instanceof Error ? (reason.stack ?? '') : '')
  }

  window.addEventListener('error', onError)
  window.addEventListener('unhandledrejection', onRejection)
  return () => {
    window.removeEventListener('error', onError)
    window.removeEventListener('unhandledrejection', onRejection)
  }
}

// ─── console.warn / console.error ────────────────────────────────────────────

function stringifyOne(a: unknown): string {
  let s: string
  if (typeof a === 'string') s = a
  else if (a instanceof Error) s = a.message
  else {
    try {
      // `JSON.stringify(undefined)` returns undefined, not a string, and a
      // function or a symbol does the same — `truncate` then throws on
      // `.length` and the capture swallows the whole event.
      s = JSON.stringify(a) ?? String(a)
    } catch {
      s = String(a)
    }
  }
  return truncate(s, ARG_MAX)
}

/**
 * Apply console format specifiers the way the browser does.
 *
 * consola styles its tag with `%c`, so a single logger call arrives here as
 * ["%capi:auth%c Verify OTP failed:", "<css>", "", err]. Joining that on a
 * space put the stylesheet INTO the message — the Telegram alert read
 * "background: #c0392b; border-radius: 0.5em; ..." and the sentence that said
 * what had failed was what the truncation then cut. Every styled log from
 * consola, and anything else using %c, was unreadable for the same reason.
 *
 * Only the specifiers a console actually consumes are handled: `%c` swallows
 * its argument and contributes nothing, `%s`/`%d`/`%i`/`%f`/`%o`/`%O`/`%j`
 * substitute theirs. `%%` is a literal percent and consumes nothing. Anything
 * left over is appended, which is what the browser does with extra arguments.
 *
 * Not applied when the first argument is not a string, or carries no
 * specifier: then there is nothing to substitute and the old join is right.
 */
export function formatConsoleArgs(args: unknown[]): string {
  const [first, ...rest] = args
  if (typeof first !== 'string' || !/%[csdifoOj%]/.test(first)) {
    return args.map(stringifyOne).join(' ')
  }

  let i = 0
  const out = first.replace(/%([csdifoOj%])/g, (match, spec: string) => {
    if (spec === '%') return '%'
    if (i >= rest.length) return match // no argument left: the browser keeps the token
    const arg = rest[i++]
    if (spec === 'c') return '' // a style, not content
    if (spec === 'd' || spec === 'i') return String(Math.trunc(Number(arg)))
    if (spec === 'f') return String(Number(arg))
    return stringifyOne(arg)
  })

  const unused = rest.slice(i).map(stringifyOne)
  return truncate([out.trim(), ...unused].filter(Boolean).join(' '), ARG_MAX * 4)
}

function stringifyArgs(args: unknown[]): string {
  return formatConsoleArgs(args)
}

export function installConsoleCapture(): () => void {
  if (typeof window === 'undefined') return () => {}

  const report = (level: 'warn' | 'error', args: unknown[]) => {
    try {
      // Generated-client diagnostics already have an event owner. Routine
      // HTTP 4xx are console-only, so do not turn them into monitor alerts.
      if (typeof args[0] === 'string' && /^\[DjangoCFG:(validation|request)\] /.test(args[0])) return
      const message = stringifyArgs(args)
      const stack = args.find((a): a is Error => a instanceof Error)?.stack
      if (isNoise(message, stack)) return
      devtoolsStore.getState().capture({
        event_type: level === 'error' ? EventType.ERROR : EventType.WARNING,
        level: level === 'error' ? EventLevel.ERROR : EventLevel.WARNING,
        message,
        stack_trace: stack,
        ...browserContext(),
      })
    } catch {
      /* never crash */
    }
  }

  const origWarn = console.warn.bind(console)
  const origError = console.error.bind(console)
  console.warn = (...args: unknown[]) => {
    origWarn(...args)
    report('warn', args)
  }
  console.error = (...args: unknown[]) => {
    origError(...args)
    report('error', args)
  }
  return () => {
    console.warn = origWarn
    console.error = origError
  }
}

// ─── zod-validation-error events (fired by @djangocfg/api clients) ──────────

interface ValidationErrorDetail {
  operation: string
  path: string
  method: string
  error: { message: string }
  reference?: string
  diagnostic?: string
}

export function installValidationCapture(): () => void {
  if (typeof window === 'undefined') return () => {}

  const handler = (event: Event) => {
    if (!(event instanceof CustomEvent)) return
    try {
      const detail = event.detail as ValidationErrorDetail
      devtoolsStore.getState().capture({
        event_type: EventType.WARNING,
        level: EventLevel.WARNING,
        message: truncate(
          `Zod validation error in ${detail.operation}: ${detail.diagnostic ?? detail.error?.message ?? 'unknown'}`,
          MSG_MAX,
        ),
        http_method: detail.method,
        http_url: detail.path,
        extra: { operation: detail.operation, path: detail.path, method: detail.method, ...(detail.reference && { reference: detail.reference }) },
        ...browserContext(),
      })
    } catch {
      /* never crash */
    }
  }

  window.addEventListener('zod-validation-error', handler)
  return () => window.removeEventListener('zod-validation-error', handler)
}

// ─── network-error events (unexpected generated-client request failures) ────

interface NetworkErrorDetail {
  method: string
  url: string
  error: string
  statusCode?: number
  possibly_cors?: boolean
  reference?: string
}

export function installNetworkCapture(): () => void {
  if (typeof window === 'undefined') return () => {}
  const handler = (event: Event) => {
    if (!(event instanceof CustomEvent)) return
    try {
      const detail = event.detail as NetworkErrorDetail
      if (INGEST_PATTERN.test(detail.url)) return
      devtoolsStore.getState().capture({
        event_type: EventType.NETWORK_ERROR,
        level: detail.statusCode && detail.statusCode >= 400 && detail.statusCode < 500 ? EventLevel.WARNING : EventLevel.ERROR,
        message: truncate(`${detail.method} ${detail.url}: ${detail.error}`, MSG_MAX),
        http_method: detail.method,
        http_url: detail.url,
        ...(typeof detail.statusCode === 'number' && { http_status: detail.statusCode }),
        extra: {
          ...(detail.reference && { reference: detail.reference }),
          ...(detail.possibly_cors && { possibly_cors: true }),
        },
        ...browserContext(),
      })
    } catch { /* never crash */ }
  }
  window.addEventListener('network-error', handler)
  return () => window.removeEventListener('network-error', handler)
}

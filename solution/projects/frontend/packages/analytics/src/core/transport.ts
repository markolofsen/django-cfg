/**
 * The batched beacon transport. THE one place this logic exists.
 *
 * Owned by @djangocfg/analytics and imported by @djangocfg/devtools, so the
 * unload-delivery rules below are implemented once rather than re-derived (and
 * re-broken) per consumer. Zero React, zero UI, zero framework — safe to import
 * from anywhere, including a vanilla capture hook.
 *
 * ─────────────────────────────────────────────────────────────────────────────
 * THE TRAP THIS EXISTS TO PREVENT
 * ─────────────────────────────────────────────────────────────────────────────
 * The obvious unload flush loses data SILENTLY:
 *
 *     navigator.sendBeacon(url, new Blob([json], { type: 'application/json' }))
 *
 * `application/json` is NOT a CORS-safelisted Content-Type, so the request
 * leaves no-cors mode and triggers an OPTIONS preflight — which, during unload,
 * usually cannot complete. The POST is never sent. `sendBeacon` still returns
 * `true`, because true means "queued", not "delivered". No error, no exception,
 * no retry. Verified in Chrome 149.
 *
 * The events you lose are the ones that mattered most: whatever crashed the page
 * and caused the navigation away.
 *
 * Rules, all of which this module encodes:
 *   1. Prefer SAME-ORIGIN ingest (Next rewrites / Vite proxy). Same-origin means
 *      no CORS and therefore no preflight, ever. It also dodges ad blockers.
 *   2. On unload, send `text/plain` — CORS-safelisted, so no preflight. The body
 *      is still JSON; only the label differs. The server reads it with an
 *      additive parser scoped to the ingest view.
 *   3. CHECK sendBeacon's boolean return and fall back to fetch(keepalive).
 *   4. Respect the 64KB keepalive quota, which is per-document and SHARED
 *      between sendBeacon and fetch(keepalive).
 */

/** Stay under the shared 64KB per-document keepalive quota. */
const KEEPALIVE_LIMIT = 60_000

export interface BeaconOptions {
  /** Where to POST. Relative keeps it same-origin — see rule 1. */
  url: string

  /**
   * Called when the queue is drained. Receives the events being sent, and must
   * return the request body. Lets each consumer keep its own payload shape.
   */
  serialize: (events: unknown[]) => string

  /** Flush automatically once the queue reaches this size. */
  batchSize?: number

  /** Send cookies, so the server can attribute events to a signed-in user. */
  credentials?: RequestCredentials
}

export class BeaconTransport {
  private queue: unknown[] = []
  private readonly url: string
  private readonly serialize: (events: unknown[]) => string
  private readonly batchSize: number
  private readonly credentials: RequestCredentials

  constructor(options: BeaconOptions) {
    this.url = options.url
    this.serialize = options.serialize
    this.batchSize = options.batchSize ?? 25
    this.credentials = options.credentials ?? 'include'
  }

  /** Queue an event, flushing automatically once the batch is full. */
  push(event: unknown): void {
    this.queue.push(event)
    if (this.queue.length >= this.batchSize) this.flush(false)
  }

  /**
   * Send what is queued.
   *
   * `final` must be true when the document is going away — it switches to a
   * delivery mechanism that survives unload. Getting this wrong is the entire
   * point of this module.
   */
  flush(final: boolean): void {
    if (this.queue.length === 0) return

    const events = this.queue.splice(0, this.batchSize)
    const body = this.serialize(events)

    if (final) {
      // A raw string (not a typed Blob) sends as text/plain, which is
      // CORS-safelisted — so no preflight, and it actually leaves the browser.
      if (body.length < KEEPALIVE_LIMIT && navigator.sendBeacon?.(this.url, body)) {
        return
      }
      // sendBeacon refused: over quota, or unavailable. keepalive is the
      // documented fallback that also outlives the document.
      void fetch(this.url, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body,
        keepalive: true,
        credentials: this.credentials,
      }).catch(() => {
        // The page is dying. There is nothing useful left to do.
      })
      return
    }

    void fetch(this.url, {
      method: 'POST',
      // Not an unload flush, so the honest content type is fine.
      headers: { 'Content-Type': 'application/json' },
      body,
      credentials: this.credentials,
    }).catch(() => {
      // Telemetry must never surface an error into the app it is measuring.
    })
  }

  /** Number of events waiting to be sent. */
  get pending(): number {
    return this.queue.length
  }
}

/**
 * The analytics client. Framework-agnostic, zero React.
 *
 * One instance owns the fan-out to every transport, plus the two pieces of
 * state that MUST be module-scoped rather than component-scoped:
 *
 *   - the dedup key (see `trackPageview`)
 *   - the flush listeners (registered once, in `init`)
 *
 * Nothing is registered at module top level: listeners attach only inside
 * `init()`. A top-level side effect would defeat `sideEffects: false` and get
 * tree-shaken in some bundlers while surviving in others — the worst kind of
 * inconsistency.
 */

import type { AnalyticsEventPayload, AnalyticsOptions, AnalyticsTransport } from './types'
import type { AnalyticsEventName, AnalyticsEventProps } from '../events'

export class AnalyticsClient {
  private transports: AnalyticsTransport[] = []
  private started = false
  private debug: boolean

  /**
   * The last pageview key we sent.
   *
   * MUST live here, not in a React ref. React 19 StrictMode remounts components
   * in development, and a `useRef` is reset by that remount — so the guard would
   * not guard. A module/instance-scoped value survives it.
   *
   * This is also what makes `router.refresh()` not count as a pageview: the URL
   * key is unchanged, so it is suppressed.
   */
  private lastPageviewKey: string | null = null

  private flushHandler?: () => void
  private pagehideHandler?: () => void

  // Engagement: did a person act, and for how long was the page visible and in use.
  // A crawler that executes JavaScript still sends pageviews but never fires one of
  // these input events, which is what separates it from a reader on the server.
  private interacted = false
  private interactionReported = false
  private activeMs = 0
  private lastTick = 0
  private lastInteractionAt = 0
  private reportedSec = 0
  private tickTimer?: number
  private engagementHandlers: Array<[EventTarget, string, EventListener, AddEventListenerOptions]> = []

  constructor(options: AnalyticsOptions) {
    this.transports = options.transports ?? []
    this.debug = options.debug ?? true
  }

  async init(): Promise<void> {
    if (this.started || typeof window === 'undefined') return
    this.started = true

    for (const t of this.transports) {
      try {
        await t.init?.()
      } catch (err) {
        // A broken transport must never break the page it is measuring.
        this.warn(`transport "${t.name}" failed to init`, err)
      }
    }

    this.registerFlushListeners()
    this.registerEngagementListeners()
  }

  /**
   * Track a pageview, unless it is a duplicate of the last one.
   *
   * The key is the full URL, so a `router.refresh()` or a StrictMode double
   * effect collapses into one event, while a real navigation always fires.
   */
  trackPageview(payload: AnalyticsEventPayload): void {
    const key = `${payload.pathname}?${payload.props?.search ?? ''}`
    if (key === this.lastPageviewKey) return
    this.lastPageviewKey = key

    this.fanOut((t) => t.pageview(payload))
  }

  trackEvent<Name extends AnalyticsEventName>(
    name: Name,
    props: AnalyticsEventProps<Name> = {} as AnalyticsEventProps<Name>,
  ): void {
    if (typeof window === 'undefined') return

    this.fanOut((t) =>
      t.event({
        event_name: name,
        pathname: window.location.pathname,
        props,
      }),
    )
  }

  /**
   * Attach (or clear) the authenticated user.
   *
   * Pass `null` on logout. A user id left attached after logout is a real
   * privacy leak — the next anonymous session inherits it.
   */
  identify(userId: string | null): void {
    this.fanOut((t) => t.identify?.(userId))
  }

  flush(final = false): void {
    this.fanOut((t) => t.flush?.(final))
  }

  destroy(): void {
    for (const [target, type, handler, opts] of this.engagementHandlers) {
      target.removeEventListener(type, handler, opts)
    }
    this.engagementHandlers = []
    if (this.tickTimer !== undefined) window.clearInterval(this.tickTimer)
    if (this.flushHandler) {
      document.removeEventListener('visibilitychange', this.flushHandler)
    }
    if (this.pagehideHandler) {
      window.removeEventListener('pagehide', this.pagehideHandler)
    }
    this.started = false
  }

  private registerFlushListeners(): void {
    // visibilitychange -> hidden is the PRIMARY signal, and pagehide is the
    // backstop.
    //
    // Deliberately NOT 'unload': it disqualifies the page from the bfcache
    // entirely. And deliberately not 'beforeunload': also bfcache-hostile, and
    // iOS Safari may never fire it at all — so a beforeunload-only flush loses
    // every mobile Safari session.
    this.flushHandler = () => {
      if (document.visibilityState === 'hidden') {
        this.reportEngagement()
        this.flush(true)
      }
    }
    this.pagehideHandler = () => {
      this.reportEngagement()
      this.flush(true)
    }

    document.addEventListener('visibilitychange', this.flushHandler)
    window.addEventListener('pagehide', this.pagehideHandler)
  }

  /**
   * Listen for input, once per document, passively. Time counts only while the tab
   * is visible and the visitor acted in the last 30 s, so a forgotten background
   * tab does not read as a ten-minute visit.
   */
  private registerEngagementListeners(): void {
    const IDLE_MS = 30_000
    const add = (target: EventTarget, type: string, handler: EventListener) => {
      const opts: AddEventListenerOptions = { passive: true, capture: true }
      target.addEventListener(type, handler, opts)
      this.engagementHandlers.push([target, type, handler, opts])
    }

    const tick = () => {
      const now = Date.now()
      if (this.lastTick && document.visibilityState === 'visible' && now - this.lastInteractionAt < IDLE_MS) {
        this.activeMs += Math.min(now - this.lastTick, 5_000)
      }
      this.lastTick = now
    }

    const onInput = () => {
      tick()
      this.lastInteractionAt = Date.now()
      this.interacted = true
      if (!this.interactionReported) {
        // Report the first action at once, so a visit that is never closed cleanly
        // (a phone locked mid-read) is still known to be a person.
        this.interactionReported = true
        this.sendEngagement(0)
      }
    }
    for (const type of ['pointerdown', 'pointermove', 'keydown', 'scroll', 'touchstart', 'wheel']) {
      add(window, type, onInput)
    }
    add(document, 'click', (e) => this.trackOutbound(e as MouseEvent))

    this.tickTimer = window.setInterval(tick, 2_000)
    this.lastTick = Date.now()
  }

  /** Send the seconds accumulated since the last report. No-op when nothing new. */
  private reportEngagement(): void {
    if (!this.interacted) return
    const total = Math.round(this.activeMs / 1000)
    const delta = total - this.reportedSec
    if (delta <= 0) return
    this.reportedSec = total
    this.sendEngagement(delta)
  }

  private sendEngagement(seconds: number): void {
    this.firstParty((t) =>
      t.event({
        event_name: 'engagement',
        pathname: window.location.pathname,
        props: { interacted: this.interacted, seconds },
      }),
    )
  }

  /** A click on a link that leaves the site: the "went to the source listing" signal. */
  private trackOutbound(e: MouseEvent): void {
    const a = (e.target as Element | null)?.closest?.('a[href]') as HTMLAnchorElement | null
    if (!a || !a.host || a.host === window.location.host) return
    if (a.protocol !== 'http:' && a.protocol !== 'https:') return
    this.firstParty((t) =>
      t.event({
        event_name: 'outbound_click',
        pathname: window.location.pathname,
        props: { host: a.host },
      }),
    )
  }

  /** Engagement is first-party telemetry; GA4 has its own, so it is not forwarded there. */
  private firstParty(fn: (t: AnalyticsTransport) => void): void {
    this.fanOut((t) => {
      if (t.name === 'djangocfg') fn(t)
    })
  }

  private fanOut(fn: (t: AnalyticsTransport) => void): void {
    for (const t of this.transports) {
      try {
        fn(t)
      } catch (err) {
        this.warn(`transport "${t.name}" threw`, err)
      }
    }
  }

  private warn(message: string, err?: unknown): void {
    if (this.debug) console.warn(`[analytics] ${message}`, err)
  }
}

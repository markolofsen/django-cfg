/**
 * Core types. No React, no framework, no DOM assumptions beyond `window`.
 */

/** A single tracked event. `pageview` is the default and most common. */
export interface AnalyticsEventPayload {
  event_name: string

  /** Raw URL path, e.g. `/en/blog/hello-world`. */
  pathname: string

  /**
   * Templated route, e.g. `/[locale]/blog/[slug]`.
   *
   * Without this, `/en/pricing` and `/ru/pricing` fragment into two separate
   * "pages" and the top-pages report is meaningless on a locale-prefixed site.
   */
  route?: string

  /** Lifted out of the path into its own dimension, for the same reason. */
  locale?: string

  hostname?: string
  page_title?: string
  referrer?: string

  utm_source?: string
  utm_medium?: string
  utm_campaign?: string
  utm_content?: string
  utm_term?: string

  click_id?: string
  click_id_param?: string

  /** Arbitrary custom properties. Stored as jsonb server-side. */
  props?: Record<string, unknown>
}

/**
 * A destination for events.
 *
 * The whole point of the package: ONE route listener fans out to N transports.
 * Before this, the GA4 layer owned its own route listener; adding a second
 * destination would have meant a second listener, double-firing with a drifting
 * taxonomy.
 */
export interface AnalyticsTransport {
  readonly name: string

  /** Called once, on init. Must not throw. */
  init?(): void | Promise<void>

  /** Record a pageview. */
  pageview(event: AnalyticsEventPayload): void

  /** Record a custom event. */
  event(event: AnalyticsEventPayload): void

  /** Attach an authenticated identity. Pass `null` on logout. */
  identify?(userId: string | null): void

  /**
   * Send anything buffered. Called on visibilitychange->hidden and pagehide.
   *
   * `final` is true when the document is going away, which is when a transport
   * must use a delivery mechanism that survives unload (sendBeacon /
   * fetch keepalive) rather than a normal fetch.
   */
  flush?(final: boolean): void
}

export interface AnalyticsOptions {
  transports: AnalyticsTransport[]

  /**
   * Track in development too.
   *
   * Defaults to TRUE, which reverses the old GA4 layer's behavior. That layer
   * was `isProd`-gated, so it was silent in dev — you could not tell whether
   * tracking worked until you shipped. Self-hosting removes the reason for that
   * gate: your own dev traffic goes to your own database, which is arguably the
   * entire point.
   */
  debug?: boolean
}

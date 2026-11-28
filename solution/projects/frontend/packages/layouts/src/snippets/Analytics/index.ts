/**
 * Analytics — MOVED to `@djangocfg/analytics`.
 *
 * This is a back-compat re-export so existing imports keep working. New code
 * should import from `@djangocfg/analytics` directly.
 *
 * Why it moved: this module used to own its own route listener. Adding a second
 * destination (the self-hosted first-party backend) would have meant a SECOND
 * listener, double-firing pageviews with a drifting event taxonomy. The new
 * package has one listener that fans out to N transports — GA4 is now just one
 * of them, alongside the django-cfg ingest endpoint.
 */

export { AnalyticsCategory, AnalyticsEvent, useAnalytics } from '@djangocfg/analytics';

export type { AnalyticsCategoryType, AnalyticsEventType } from '@djangocfg/analytics';

export { AnalyticsProvider } from './AnalyticsProvider';
export type { AnalyticsConfig } from './types';

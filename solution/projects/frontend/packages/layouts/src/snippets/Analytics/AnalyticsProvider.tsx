'use client';

/**
 * The layouts adapter for `@djangocfg/analytics`.
 *
 * BaseApp mounts this inside AuthProvider, which is what lets it attach the
 * signed-in user's id — the thing hosted analytics (Plausible, Umami, GA4
 * without extra plumbing) structurally cannot do.
 *
 * Transports are composed here:
 *   - `djangocfg` — always on. Same-origin, self-hosted, no third party.
 *   - `ga4`       — only when a tracking id is configured.
 *
 * Note the behavior change from the old implementation: that one hard-gated on
 * `isProd`, so it was completely silent in development and you could not tell
 * whether tracking worked until you shipped. Self-hosting removes the reason for
 * that gate — your dev traffic goes to your own database.
 */

import { ReactNode, useEffect, useMemo } from 'react';

import {
  AnalyticsProvider as BaseAnalyticsProvider,
  PageviewTracker,
  djangocfg,
  ga4,
  useAnalyticsClient,
  type AnalyticsTransport,
} from '@djangocfg/analytics';
import { auth as authStore } from '@djangocfg/api';
import { setAnalyticsSink, useAuth } from '@djangocfg/api/auth';
import { useLocaleOptional } from '@djangocfg/i18n';

import { usePathnameWithoutLocale } from '../../hooks/usePathnameWithoutLocale';

interface AnalyticsProviderProps {
  children: ReactNode;
  /** GA4 measurement ID. Omit to run first-party only. */
  trackingId?: string;
  /**
   * Templated route (`/[locale]/blog/[slug]`). Next does not expose it to client
   * components, so an app can pass it for exact grouping. Optional: without it
   * the locale-stripped pathname is used, which already prevents the worst
   * failure (see below).
   */
  route?: string;
}

export function AnalyticsProvider({
  children,
  trackingId,
  route,
}: AnalyticsProviderProps) {
  const { user } = useAuth();

  // The locale is READ here rather than passed in by every app.
  //
  // It matters: without it, `/en/pricing` and `/ru/pricing` are counted as two
  // different pages, and the top-pages report is meaningless on a
  // locale-prefixed site. `useLocaleOptional` returns undefined (rather than
  // throwing) in an app with no i18n, so this stays safe for both.
  // `?? undefined` is load-bearing: useLocaleOptional returns `null` with no
  // I18nProvider, and this package builds with `strict: false`, so a raw null
  // would sail through the `locale?: string` prop and end up in the payload.
  const locale = useLocaleOptional() ?? undefined;

  // The locale-stripped path is the fallback "route". Not as good as the real
  // templated route (`/blog/[slug]` still fragments per slug), but it fixes the
  // locale split with zero work from the app.
  const strippedPath = usePathnameWithoutLocale(locale);

  const transports = useMemo<AnalyticsTransport[]>(() => {
    const list: AnalyticsTransport[] = [
      djangocfg({ getAuthToken: () => authStore.getToken() }),
    ];
    if (trackingId) list.push(ga4({ trackingId }));
    return list;
  }, [trackingId]);

  return (
    <BaseAnalyticsProvider
      transports={transports}
      // An opaque id — never an email. Goes back to null on logout, or the next
      // anonymous session would inherit it.
      userId={user?.id != null ? String(user.id) : null}
    >
      <AuthEventBridge />
      <PageviewTracker route={route ?? strippedPath} locale={locale} />
      {children}
    </BaseAnalyticsProvider>
  );
}

/**
 * Routes `@djangocfg/api`'s auth events into the analytics client.
 *
 * `api` cannot import `analytics` (analytics reads auth state — that would be a
 * cycle), so `api` exposes a sink and we install the real implementation here,
 * where both packages are already in scope.
 *
 * Without this bridge, every auth event — AUTH_LOGIN_SUCCESS, AUTH_OAUTH_FAIL,
 * AUTH_SESSION_EXPIRED — hits api's built-in no-op stub and is silently
 * discarded. That was the status quo before this package existed.
 */
function AuthEventBridge() {
  const client = useAnalyticsClient();

  useEffect(() => {
    if (!client) return;

    setAnalyticsSink({
      event: (name, params) => client.trackEvent(name, params),
      setUser: (userId) => client.identify(userId),
    });

    // Uninstall on unmount, or a torn-down client keeps receiving events.
    return () => setAnalyticsSink(null);
  }, [client]);

  return null;
}

export default AnalyticsProvider;

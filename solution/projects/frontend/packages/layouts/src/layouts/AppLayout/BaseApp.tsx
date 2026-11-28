/**
 * BaseApp - Core Providers Wrapper
 *
 * The canonical provider stack for ANY React host — it is framework-agnostic and
 * does NOT depend on Next.js routing. Use it directly as the single top-level
 * wrapper in environments that have no Next.js app router: **Wails desktop**,
 * Electron, Vite/SPA, plain React. (In Next.js apps it's mounted once in the
 * root `[locale]/layout.tsx`; per-route shells are chosen by native route-group
 * `layout.tsx` files, not by this component.)
 *
 * Provides essential app-wide providers:
 * - ThemeProvider (light/dark/system theme)
 * - TooltipProvider (tooltip positioning)
 * - QueryClientProvider (React Query: the app's own client, one above, or one with django-cfg's defaults)
 * - AuthProvider (authentication context)
 * - RealtimeProvider (`@djangocfg/realtime`, lazy: no socket until a `useTopic` mounts)
 * - AuthDialog (global auth prompt dialog)
 * - AnalyticsProvider (Google Analytics, optional)
 * - LocaleSuggestion (offers the visitor's language when `i18n` has several locales)
 * - PwaProvider (PWA installation, optional)
 * - ErrorTrackingProvider (error handling)
 * - ErrorBoundary (React error boundary, enabled by default)
 *
 * @example
 * ```tsx
 * import { BaseApp } from '@djangocfg/layouts';
 *
 * // With PWA Install
 * <BaseApp
 *   theme={{ defaultTheme: 'system' }}
 *   auth={{ loginPath: '/auth/login' }}
 *   analytics={{ googleTrackingId: 'G-XXXXXXXXXX' }}
 *   pwaInstall={{ enabled: true, logo: '/logo192.png' }}
 * >
 *   {children}
 * </BaseApp>
 *
 * // To disable ErrorBoundary:
 * <BaseApp errorBoundary={{ enabled: false }}>
 *   {children}
 * </BaseApp>
 * ```
 */

'use client';

import { nodeEnv } from "@djangocfg/ui-core/lib";

import { Devtools, devtools } from '@djangocfg/devtools';
import { errorDetailToDevtoolsEvent } from '../../components/errors/ErrorsTracker';
import { AuthProvider } from '@djangocfg/api/auth';
import { UiProviders } from '@djangocfg/ui-core/providers';
import { useScrollToTop } from '@djangocfg/ui-core/hooks';
import { NextRouterAdapter, NextLinkProvider } from '@djangocfg/ui-core/adapters/nextjs';
import { RouteProgressProvider } from '@djangocfg/ui-core/route-progress';
import { NextIntlLinkBridge } from './NextIntlLinkBridge';
import { ThemeProvider } from '@djangocfg/ui-core/theme';
import { AppErrorFallback } from '../../components/errors/AppErrorFallback';
import { reportRenderError } from '../../components/errors/reportRenderError';
import { ErrorTrackingProvider } from '../../components/errors/ErrorsTracker';
import { AnalyticsProvider } from '../../snippets/Analytics';
import { AuthDialog } from '../../snippets/AuthDialog';

import type { BaseLayoutProps } from '../types/layout.types';
import { LayoutI18nProvider } from '../../shared/LayoutI18nProvider';
import { LocaleSuggestion } from '../../components/LocaleSuggestion';
import { ProjectNameProvider } from '../../shared/ProjectContext';
import { PwaManifestCheck, PwaMetaGuard } from './pwaMeta';
import { resolveDevtoolsBaseUrl } from './devtoolsBaseUrl';
import { RealtimeMount } from './realtime/RealtimeMount';
import { AppQueryProvider } from './query/AppQueryProvider';
import { resolveRealtimeApiUrl } from './realtime/realtimeApiUrl';

import React from 'react';

// For backwards compatibility, re-export as BaseAppProps
export type BaseAppProps = BaseLayoutProps;

/**
 * Lands every forward navigation at the top of the page.
 *
 * Mounted here rather than left to each app because the gap it covers is in
 * the ROUTER, not in any one project: Next's App Router abandons its scroll
 * silently when a route's first DOM node has no box (a `display: contents`
 * wrapper, a JSON-LD script, a component returning `null`) or when that node
 * already sits in the viewport. Every app built on this stack hits it, and
 * the symptom — a new page opening halfway down — reads as a broken link.
 *
 * Its own component so the hook subscribes below the router adapter and
 * re-runs nothing above it. See `useScrollToTop` for what it leaves alone
 * (back/forward, `#hash` targets, query-only writes).
 */
function ScrollToTop() {
  useScrollToTop();
  return null;
}

/** Inside `AuthProvider` so a login or logout reconnects the socket with the new identity. */
function OptionalRealtime({
  config,
  apiUrl,
  children,
}: {
  config: BaseAppProps['realtime'];
  apiUrl: string | undefined;
  children: React.ReactNode;
}) {
  if (config === false || config === undefined) return <>{children}</>;
  return (
    <RealtimeMount config={config} apiUrl={apiUrl}>
      {children}
    </RealtimeMount>
  );
}

/**
 * BaseApp - Core providers wrapper for any React/Next.js app
 *
 * Includes: ThemeProvider, TooltipProvider, QueryClientProvider, AuthProvider, AnalyticsProvider,
 * ErrorTrackingProvider, ErrorBoundary (optional)
 * Also renders global Toaster and PageProgress components
 */
export function BaseApp({
  children,
  project,
  theme,
  auth,
  apiUrl,
  analytics,
  errorTracking,
  errorBoundary,
  queryClient,
  queryDevtools,
  devtools: devtoolsConfig,
  i18n,
  pwaMeta = true,
  progressBar = true,
  realtime = {},
  debug,
}: BaseAppProps) {
  // auth=false disables AuthProvider entirely (public apps with no login)
  const authEnabled = auth !== false;
  const authConfig = auth === false ? undefined : auth;

  // ErrorBoundary is enabled by default
  const enableErrorBoundary = errorBoundary?.enabled !== false;

  // Devtools — capture + ingest + debug panel in one component.
  // Project prop is the default; the devtools prop overrides field by field.
  const devtoolsProps = {
    project,
    environment: nodeEnv,
    ...devtoolsConfig,
    baseUrl: resolveDevtoolsBaseUrl({ auth, apiUrl, devtools: devtoolsConfig }),
  };

  const realtimeApiUrl = resolveRealtimeApiUrl({ auth, apiUrl, realtime });

  const content = (
    <>
    {pwaMeta && <PwaMetaGuard />}
    {pwaMeta && <PwaManifestCheck />}
    <ThemeProvider
      defaultTheme={theme?.defaultTheme || 'system'}
      storageKey={theme?.storageKey}
    >
      {/*
       * NextRouterAdapter wires @djangocfg/ui-core router hooks
       * (useNavigate, useQueryState, etc.) to next/navigation so
       * server components, route loaders, and prefetch fire
       * correctly. Placed near the top so every provider below
       * (Auth, anything that may navigate) gets it.
       */}
      <RouteProgressProvider
        enabled={progressBar !== false}
        {...(typeof progressBar === 'object' ? progressBar : {})}
      >
      <NextRouterAdapter>
      <NextLinkProvider>
      {/* Single top-level boundary lives inside UiProviders. We feed it the
          app's i18n fallback + onError instead of wrapping our own boundary on
          top — one catch in the tree. errorBoundary={false} fully disables it
          when the host opts out. */}
      <UiProviders
        debug={debug}
        errorBoundary={enableErrorBoundary ? undefined : false}
        onError={(error, info) => {
          // The boundary swallows the error, so devtools' window.onerror never sees it:
          // report it here, then let the host's own handler run.
          reportRenderError('app-boundary', error, info);
          errorBoundary?.onError?.(error, info);
        }}
        errorFallback={
          enableErrorBoundary
            ? () => <AppErrorFallback supportEmail={errorBoundary?.supportEmail} />
            : undefined
        }
      >
        <AppQueryProvider queryClient={queryClient} queryDevtools={queryDevtools}>
          <AuthProvider config={authEnabled ? authConfig : undefined} enabled={authEnabled}>
            <OptionalRealtime config={realtime} apiUrl={realtimeApiUrl}>
            <AnalyticsProvider trackingId={analytics?.googleTrackingId}>
              <ErrorTrackingProvider
                validation={errorTracking?.validation}
                cors={errorTracking?.cors}
                network={errorTracking?.network}
                onError={errorTracking?.onError}
                onMonitorCapture={(d) => {
                  // Devtools owns the generated-client validation and network events.
                  // Do not create a second monitoring row.
                  if (d.type !== 'validation' && d.type !== 'network') devtools.capture(errorDetailToDevtoolsEvent(d));
                }}
              >
                <ScrollToTop />
                <Devtools {...devtoolsProps} />
                <LayoutI18nProvider value={i18n}>
                  <ProjectNameProvider value={project}>
                    {i18n?.routing ? (
                      <NextIntlLinkBridge routing={i18n.routing}>{children}</NextIntlLinkBridge>
                    ) : (
                      children
                    )}
                    <LocaleSuggestion />
                  </ProjectNameProvider>
                </LayoutI18nProvider>
                {/* Auth Dialog - only when auth is enabled */}
                {authEnabled && <AuthDialog authPath={authConfig?.routes?.auth} />}
              </ErrorTrackingProvider>
            </AnalyticsProvider>
            </OptionalRealtime>
          </AuthProvider>
        </AppQueryProvider>
      </UiProviders>
      </NextLinkProvider>
      </NextRouterAdapter>
      </RouteProgressProvider>
    </ThemeProvider>
    </>
  );

  // The error boundary is now UiProviders' built-in one (fed our i18n fallback
  // + onError above) — no outer wrapper needed.
  return content;
}

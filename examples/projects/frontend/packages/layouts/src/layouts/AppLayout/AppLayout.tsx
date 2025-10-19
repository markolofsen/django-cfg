/**
 * AppLayout - Unified Application Layout System
 *
 * Single component that handles all layout logic:
 * - Auto-detects route type (public/private/auth)
 * - Applies correct layout automatically
 * - Manages all state through context
 * - Zero prop drilling
 *
 * Usage in _app.tsx:
 * ```tsx
 * <AppLayout config={appLayoutConfig}>
 *   <Component {...pageProps} />
 * </AppLayout>
 * ```
 */

'use client';

import React, { ReactNode, useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { AppContextProvider } from './context';
import { CoreProviders } from './providers';
import { Seo, PageProgress, ErrorBoundary } from './components';
import { PublicLayout } from './layouts/PublicLayout';
import { PrivateLayout } from './layouts/PrivateLayout';
import { AuthLayout } from './layouts/AuthLayout';
import { determineLayoutMode, getRedirectUrl } from './utils';
import { useAuth } from '../../auth';
import type { AppLayoutConfig } from './types';

export interface AppLayoutProps {
  children: ReactNode;
  config: AppLayoutConfig;
  /**
   * Disable layout rendering (Navigation, Sidebar, Footer)
   * Only providers and SEO remain active
   * Useful for custom layouts like landing pages
   */
  disableLayout?: boolean;
  /**
   * Force a specific layout regardless of route
   * Overrides automatic layout detection
   * @example forceLayout="public" - always use PublicLayout
   */
  forceLayout?: 'public' | 'private' | 'auth';
  /**
   * Font family to apply globally
   * Accepts Next.js font object or CSS font-family string
   * @example fontFamily={manrope.style.fontFamily}
   * @example fontFamily="Inter, sans-serif"
   */
  fontFamily?: string;
}

/**
 * Layout Router Component
 *
 * Determines which layout to use based on route
 * Uses AppContext - no props passed down!
 */
function LayoutRouter({
  children,
  disableLayout,
  forceLayout,
  config
}: {
  children: ReactNode;
  disableLayout?: boolean;
  forceLayout?: 'public' | 'private' | 'auth';
  config: AppLayoutConfig;
}) {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  const [isMounted, setIsMounted] = useState(false);

  // SSR/Hydration protection
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // If layout is disabled, render children directly (providers still active!)
  if (disableLayout) {
    return <>{children}</>;
  }

  // Determine layout mode based on route (synchronous - works with SSR)
  const getLayoutMode = (): 'public' | 'private' | 'auth' => {
    // If forceLayout is specified, use it
    if (forceLayout) return forceLayout;

    const isAuthRoute = config.routes.detectors.isAuthRoute(router.pathname);
    const isPrivateRoute = config.routes.detectors.isPrivateRoute(router.pathname);
    // const isPublicRoute = config.routes.detectors.isPublicRoute(router.pathname);

    if (isAuthRoute) return 'auth';

    if (isPrivateRoute) {
      if (isAuthenticated) {
        return 'private';
      };
      return 'auth';
    };

    return 'public';
  };

  const layoutMode = getLayoutMode();

  // Render appropriate layout
  switch (layoutMode) {
    // Public routes: render immediately (SSR enabled)
    case 'public':
      return <PublicLayout>{children}</PublicLayout>;

    // Auth routes: render inside AuthLayout
    case 'auth':
      return (
        <AuthLayout
          termsUrl={config.auth?.termsUrl}
          privacyUrl={config.auth?.privacyUrl}
          supportUrl={config.auth?.supportUrl}
          enablePhoneAuth={config.auth?.enablePhoneAuth}
        >
          {children}
        </AuthLayout>
      );

    // Private routes: wait for client-side hydration and auth check
    case 'private':
      if (!isMounted || isLoading) {
        return (
          <div className="min-h-screen flex items-center justify-center">
            <div className="text-muted-foreground">Loading...</div>
          </div>
        );
      }
      return <PrivateLayout>{children}</PrivateLayout>;
  }
}

/**
 * AppLayout - Main Component
 *
 * Single entry point for all layout logic
 * Wrap your app once in _app.tsx
 *
 * @example
 * ```tsx
 * // With layout (default - auto-detect)
 * <AppLayout config={appLayoutConfig}>
 *   <Component {...pageProps} />
 * </AppLayout>
 *
 * // With custom font
 * <AppLayout config={appLayoutConfig} fontFamily={manrope.style.fontFamily}>
 *   <Component {...pageProps} />
 * </AppLayout>
 *
 * // Without layout (providers still active)
 * <AppLayout config={appLayoutConfig} disableLayout>
 *   <CustomLandingPage />
 * </AppLayout>
 *
 * // Force public layout for all pages
 * <AppLayout config={appLayoutConfig} forceLayout="public">
 *   <Component {...pageProps} />
 * </AppLayout>
 * ```
 */
export function AppLayout({ children, config, disableLayout = false, forceLayout, fontFamily }: AppLayoutProps) {
  const router = useRouter();

  // Check if ErrorBoundary is enabled (default: true)
  const enableErrorBoundary = config.errors?.enableErrorBoundary !== false;
  const supportEmail = config.errors?.supportEmail;
  const onError = config.errors?.onError;

  const content = (
    <>
      {/* Global Font Styles */}
      {fontFamily && (
        <style dangerouslySetInnerHTML={{
          __html: `html { font-family: ${fontFamily}; }`
        }} />
      )}

      <CoreProviders config={config}>
        <AppContextProvider config={config}>
          {/* SEO Meta Tags */}
          <Seo
            pageConfig={{
              title: config.app.name,
              description: config.app.description,
              ogImage: {
                title: config.app.name,
                subtitle: config.app.description,
              },
            }}
            icons={config.app.icons}
            siteUrl={config.app.siteUrl}
          />

          {/* Loading Progress Bar */}
          <PageProgress />

          {/* Smart Layout Router */}
          <LayoutRouter disableLayout={disableLayout} forceLayout={forceLayout} config={config}>
            {children}
          </LayoutRouter>
        </AppContextProvider>
      </CoreProviders>
    </>
  );

  // Wrap with ErrorBoundary if enabled
  if (enableErrorBoundary) {
    return (
      <ErrorBoundary
        key={router.pathname}
        supportEmail={supportEmail}
        onError={onError}
      >
        {content}
      </ErrorBoundary>
    );
  }

  return content;
}

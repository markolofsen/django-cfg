'use client';

import { useEffect } from 'react';

import { useAuth } from '@djangocfg/api/auth';
import { Preloader } from '@djangocfg/ui-core/components';
import { useCfgRouter } from '@djangocfg/api/auth';

export interface RedirectPageProps {
  /**
   * Path to redirect to when user is authenticated
   * @default '/private'
   */
  authenticatedPath?: string;
  /**
   * Path to redirect to when user is not authenticated
   * @default '/auth'
   */
  unauthenticatedPath?: string;
  /**
   * Custom loading text
   * @default 'Loading...'
   */
  loadingText?: string;
}

/**
 * RedirectPage - Root page component that handles authentication redirect
 *
 * Redirects authenticated users to authenticatedPath, otherwise to unauthenticatedPath
 *
 * Usage:
 * ```tsx
 * // app/page.tsx
 * import { RedirectPage } from '@djangocfg/layouts/components';
 *
 * export default function Page() {
 *   return (
 *     <RedirectPage
 *       authenticatedPath="/private"
 *       unauthenticatedPath="/auth"
 *     />
 *   );
 * }
 * ```
 */
export function RedirectPage({
  authenticatedPath = '/private',
  unauthenticatedPath,
  loadingText = 'Loading...',
}: RedirectPageProps) {
  const { isAuthenticated, routes } = useAuth();
  const router = useCfgRouter();
  const resolvedUnauthPath = unauthenticatedPath ?? routes.auth;

  useEffect(() => {
    if (!isAuthenticated) {
      router.hardPush(resolvedUnauthPath);
    } else {
      router.hardPush(authenticatedPath);
    }
  }, [isAuthenticated, router, authenticatedPath, resolvedUnauthPath]);

  return (
    <Preloader
      variant="fullscreen"
      text={loadingText}
      size="lg"
    />
  );
}


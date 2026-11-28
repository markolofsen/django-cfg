/**
 * ClientOnly Component
 *
 * Renders children only on the client side to prevent SSR hydration mismatch.
 * Shows a fallback (loading state) during SSR and initial client mount.
 *
 * @example
 * ```tsx
 * import { ClientOnly } from '@djangocfg/layouts/components';
 *
 * // With default loading fallback
 * <ClientOnly>
 *   <ComponentThatUsesClientOnlyAPIs />
 * </ClientOnly>
 *
 * // With custom fallback
 * <ClientOnly fallback={<MyCustomLoader />}>
 *   <ComponentThatUsesClientOnlyAPIs />
 * </ClientOnly>
 * ```
 */

'use client';

import { ReactNode, useEffect, useState } from 'react';

import { Preloader } from '@djangocfg/ui-core/components';

export interface ClientOnlyProps {
  children: ReactNode;
  /**
   * Fallback to show during SSR and initial mount
   * @default Preloader with "Loading..." text
   */
  fallback?: ReactNode;
}

/**
 * Default fallback - fullscreen preloader
 */
const defaultFallback = (
  <Preloader
    variant="fullscreen"
    text="Loading..."
    size="lg"
    backdrop={true}
    backdropOpacity={80}
  />
);

/**
 * ClientOnly - Prevents SSR hydration mismatch
 *
 * Use this to wrap components that:
 * - Access browser-only APIs (window, localStorage, etc.)
 * - Have different initial state on server vs client
 * - Use authentication state that differs between SSR and CSR
 */
export function ClientOnly({
  children,
  fallback = defaultFallback,
}: ClientOnlyProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}

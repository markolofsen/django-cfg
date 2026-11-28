/**
 * i18n Navigation Utilities
 *
 * Provides locale-aware navigation components and functions
 *
 * @example
 * ```ts
 * // In your app's i18n/navigation.ts
 * import { createNavigation } from '@djangocfg/nextjs/i18n';
 * import { routing } from './routing';
 *
 * export const { Link, redirect, usePathname, useRouter } = createNavigation(routing);
 * ```
 *
 * @example
 * ```tsx
 * // Using in components
 * import { Link, usePathname } from '@/i18n/navigation';
 *
 * function Nav() {
 *   const pathname = usePathname();
 *   return <Link href="/about">About</Link>;
 * }
 * ```
 */

import { createNavigation as createNextIntlNavigation } from 'next-intl/navigation';

import { createRouting, routing } from './routing';

import type { I18nConfig } from './types';

// ─────────────────────────────────────────────────────────────────────────────
// Navigation Factory
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Create navigation utilities with custom routing
 *
 * Returns locale-aware versions of:
 * - Link: Locale-prefixed links
 * - redirect: Server-side redirect with locale
 * - usePathname: Current pathname without locale prefix
 * - useRouter: Router with locale-aware navigation
 * - getPathname: Get pathname for a route
 */
export function createNavigation(routingConfig?: ReturnType<typeof createRouting>) {
  const config = routingConfig ?? routing;
  return createNextIntlNavigation(config);
}

/**
 * Create navigation from config options
 */
export function createNavigationFromConfig(config: Partial<I18nConfig>) {
  const routingConfig = createRouting(config);
  return createNextIntlNavigation(routingConfig);
}

// ─────────────────────────────────────────────────────────────────────────────
// Default Navigation (using default routing)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Default navigation utilities
 * Use these directly or create custom ones with createNavigation()
 */
export const {
  Link,
  redirect,
  usePathname,
  useRouter,
  getPathname,
} = createNavigation();

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Props for locale-aware Link component
 */
export interface LinkProps {
  /** Target href */
  href: string;
  /** Target locale (optional, defaults to current) */
  locale?: string;
  /** Children */
  children?: React.ReactNode;
  /** Additional props passed to Next.js Link */
  [key: string]: unknown;
}

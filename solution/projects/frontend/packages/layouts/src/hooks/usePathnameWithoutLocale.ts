'use client';

import { usePathname } from 'next/navigation';
import { useMemo } from 'react';

/**
 * Normalize pathname: remove trailing slash except for root "/".
 * Works regardless of Next.js trailingSlash config.
 */
function normalize(p: string): string {
  return p.length > 1 ? p.replace(/\/+$/, '') : p;
}

/**
 * Strip locale prefix from pathname using known locale string.
 */
function stripLocale(pathname: string, locale: string): string {
  const prefix = '/' + locale;
  if (pathname === prefix || pathname === prefix + '/') return '/';
  if (pathname.startsWith(prefix + '/')) return pathname.slice(prefix.length);
  // Path already has no locale prefix (next-intl localePrefix:'as-needed' for default locale)
  return pathname;
}

/**
 * usePathnameWithoutLocale
 *
 * Returns the current pathname without locale prefix, normalized (no trailing slash).
 *
 * Pass `locale` (from i18n config / useLocaleSwitcher) for exact stripping.
 * Without locale, falls back to regex — known to misfire on 2-letter path segments like /ui.
 *
 * @example
 * // URL: /en/ui/playground, locale="en"  →  "/ui/playground"
 * // URL: /ui/playground/ (no prefix)     →  "/ui/playground"
 */
export function usePathnameWithoutLocale(locale?: string): string {
  const pathname = usePathname();

  return useMemo(() => {
    if (locale) {
      return normalize(stripLocale(pathname, locale));
    }

    // Fallback regex — only when locale is unknown
    const match = pathname.match(/^\/[a-z]{2}(-[A-Z]{2})?(\/|$)/);
    if (match) {
      const rest = pathname.slice(match[0].length - 1) || '/';
      const withSlash = rest.startsWith('/') ? rest : '/' + rest;
      return normalize(withSlash);
    }

    return normalize(pathname);
  }, [pathname, locale]);
}

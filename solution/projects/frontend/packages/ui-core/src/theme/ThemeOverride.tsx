/**
 * ThemeOverride - Pathname-aware forced theme
 *
 * Applies a forced `light` or `dark` theme via `next-themes` while the current
 * pathname matches any of the supplied rules, and restores the user's prior
 * choice when the pathname no longer matches.
 *
 * Unlike `ForceTheme` (which scopes CSS vars to a wrapper div), this component
 * mutates the real `next-themes` value — so the `html.dark` class is applied
 * and every surface (navbar, footer, body, page) picks the new theme up
 * consistently.
 *
 * The matcher is **dependency-free** and understands:
 * - Exact match (`/` matches `/`)
 * - Prefix match (`/docs` matches `/docs/getting-started`)
 * - Glob wildcards (`*` for a single segment, `**` for any depth)
 *
 * Consumers pass the pathname already stripped of the locale prefix — matching
 * is not locale-aware here.
 *
 * @example
 * ```tsx
 * <ThemeOverride
 *   pathname={pathname}
 *   rules={[
 *     { path: '/', theme: 'dark' },
 *     { path: ['/legal', '/legal/**'], theme: 'light' },
 *   ]}
 * />
 * ```
 */

'use client';

import { useEffect, useMemo, useRef } from 'react';

import { useThemeContext } from './ThemeProvider';

import type { Theme } from './ThemeProvider';

export type ForcedTheme = Exclude<Theme, 'system'>;

export interface ThemeOverrideRule {
  /** Path (or array of paths) to match against. Supports `*` and `**` globs. */
  path: string | string[];
  /** Theme to apply while the path matches. */
  theme: ForcedTheme;
}

export interface ThemeOverrideProps {
  /** Pathname stripped of locale prefix. Use `usePathnameWithoutLocale()` if you have it. */
  pathname: string;
  /** Rules evaluated top-to-bottom — first match wins. */
  rules?: ThemeOverrideRule[];
}

/**
 * Resolve the first matching rule's forced theme for a pathname, or `null`.
 * Pure helper — use this to render a `ForcedThemeProvider` in the same tree
 * where you mount `ThemeOverride`.
 */
export function resolveForcedTheme(
  pathname: string,
  rules?: ThemeOverrideRule[],
): ForcedTheme | null {
  if (!rules || rules.length === 0) return null;
  for (const rule of rules) {
    if (matchesAny(pathname, rule.path)) return rule.theme;
  }
  return null;
}

// --- inlined matcher (no dep on @djangocfg/layouts) -------------------------

function matchGlob(pathname: string, pattern: string): boolean {
  const pathParts = pathname.replace(/\/+$/, '').split('/').filter(Boolean);
  const patternParts = pattern.replace(/\/+$/, '').split('/').filter(Boolean);

  let pi = 0;
  let ti = 0;

  while (ti < patternParts.length && pi < pathParts.length) {
    const pat = patternParts[ti];
    if (pat === '**') {
      if (ti === patternParts.length - 1) return true;
      const next = patternParts[ti + 1];
      while (pi < pathParts.length) {
        if (pathParts[pi] === next || next === '*') break;
        pi++;
      }
      ti++;
    } else if (pat === '*') {
      pi++;
      ti++;
    } else {
      if (pathParts[pi] !== pat) return false;
      pi++;
      ti++;
    }
  }

  if (ti < patternParts.length) {
    for (let i = ti; i < patternParts.length; i++) {
      if (patternParts[i] !== '**') return false;
    }
  }

  return pi === pathParts.length;
}

function matchOne(pathname: string, pattern: string): boolean {
  const p = pathname.length > 1 ? pathname.replace(/\/+$/, '') : pathname;
  const q = pattern.length > 1 ? pattern.replace(/\/+$/, '') : pattern;
  if (q.includes('*')) return matchGlob(p, q);
  return p === q || p.startsWith(q + '/');
}

function matchesAny(pathname: string, path: string | string[]): boolean {
  return Array.isArray(path) ? path.some((p) => matchOne(pathname, p)) : matchOne(pathname, path);
}

// --- component --------------------------------------------------------------

export function ThemeOverride({ pathname, rules }: ThemeOverrideProps) {
  const { theme, setTheme } = useThemeContext();

  // First rule whose path matches the current pathname. null = no override.
  const forced = useMemo<ForcedTheme | null>(
    () => resolveForcedTheme(pathname, rules),
    [pathname, rules],
  );

  // Stash the user's own pick so we can restore it when they leave a forced route.
  // We capture only non-override theme values (from renders where `forced === null`).
  // Stored as a ref so it doesn't drive the effect.
  const userThemeRef = useRef<string | undefined>(undefined);

  // Keep userThemeRef in sync with what next-themes reports **while not forcing**.
  // Every render where the route isn't overridden, the current `theme` IS the user's
  // own pick — snapshot it. During a forced render we leave the ref alone so the
  // original value survives until we hand control back.
  useEffect(() => {
    if (forced === null && theme) {
      userThemeRef.current = theme;
    }
  }, [forced, theme]);

  // Apply / revert the forced theme. Intentionally driven only by `forced` — the
  // user may toggle the theme manually while forcing is off, and that's fine
  // (the sync effect above records the new value).
  useEffect(() => {
    if (forced) {
      setTheme(forced);
      return;
    }
    const restore = userThemeRef.current ?? 'system';
    setTheme(restore);
    // setTheme from next-themes is stable by ref; omit on purpose.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [forced]);

  return null;
}

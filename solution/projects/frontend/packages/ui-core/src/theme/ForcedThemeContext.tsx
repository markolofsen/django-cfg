/**
 * ForcedThemeContext
 *
 * Published by `ThemeOverride` so downstream UI (theme switchers, toggles,
 * indicators) can tell whether the current route forces a specific theme and
 * adapt accordingly — typically by disabling or hiding their controls.
 *
 * Default value is `null` (no override) — consumers outside a `ThemeOverride`
 * mount see the same shape as consumers on an unforced route, so there's no
 * need to guard against the provider being absent.
 */

'use client';

import { createContext, useContext, type ReactNode } from 'react';

import type { ForcedTheme } from './ThemeOverride';

const ForcedThemeContext = createContext<ForcedTheme | null>(null);

interface ForcedThemeProviderProps {
  value: ForcedTheme | null;
  children: ReactNode;
}

export function ForcedThemeProvider({ value, children }: ForcedThemeProviderProps) {
  return (
    <ForcedThemeContext.Provider value={value}>
      {children}
    </ForcedThemeContext.Provider>
  );
}

/**
 * Read the currently-forced theme. `null` means the user is free to choose.
 *
 * @example
 * ```tsx
 * const forced = useForcedTheme();
 * if (forced) return <p>Theme is locked to {forced} on this page.</p>;
 * ```
 */
export function useForcedTheme(): ForcedTheme | null {
  return useContext(ForcedThemeContext);
}

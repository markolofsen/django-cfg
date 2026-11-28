/**
 * ThemeProvider - Universal theme management
 *
 * Re-exports next-themes ThemeProvider with sensible defaults.
 * Supports light, dark, and system themes with localStorage persistence.
 *
 * Framework-agnostic: works in any React app (Electron, Vite, Next.js).
 *
 * @example
 * ```tsx
 * import { ThemeProvider } from '@djangocfg/ui-core/theme';
 *
 * <ThemeProvider
 *   attribute="class"
 *   defaultTheme="system"
 *   enableSystem
 * >
 *   {children}
 * </ThemeProvider>
 * ```
 */

'use client';

import { ThemeProvider as NextThemesProvider, useTheme as useNextTheme } from 'next-themes';

import type { ThemeProviderProps as NextThemesProviderProps } from 'next-themes';

// Re-export types
export type Theme = 'light' | 'dark' | 'system';
export type ThemeProviderProps = NextThemesProviderProps;

/**
 * ThemeProvider wraps next-themes with sensible defaults
 */
export function ThemeProvider({
  children,
  attribute = 'class',
  defaultTheme = 'system',
  enableSystem = true,
  disableTransitionOnChange = true,
  ...props
}: ThemeProviderProps) {
  return (
    <NextThemesProvider
      attribute={attribute}
      defaultTheme={defaultTheme}
      enableSystem={enableSystem}
      disableTransitionOnChange={disableTransitionOnChange}
      {...props}
    >
      {children}
    </NextThemesProvider>
  );
}

/**
 * Hook to access theme context
 * Returns theme, setTheme, resolvedTheme, systemTheme, and themes
 */
export function useThemeContext() {
  const { theme, setTheme, resolvedTheme, systemTheme, themes } = useNextTheme();

  const toggleTheme = () => {
    // Toggle between light and dark (ignore system)
    const currentResolved = resolvedTheme || 'light';
    setTheme(currentResolved === 'light' ? 'dark' : 'light');
  };

  return {
    theme: theme as Theme | undefined,
    setTheme,
    resolvedTheme: resolvedTheme as 'light' | 'dark' | undefined,
    systemTheme: systemTheme as 'light' | 'dark' | undefined,
    themes,
    toggleTheme,
  };
}

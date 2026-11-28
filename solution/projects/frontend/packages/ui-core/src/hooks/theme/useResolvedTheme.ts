'use client';

import { useEffect, useState } from 'react';

export type ResolvedTheme = 'light' | 'dark';

/**
 * Detect the current resolved theme (light or dark).
 *
 * Standalone hook — does not require ThemeProvider. Resolution order:
 *  1. Explicit `dark` / `light` class on `<html>`.
 *  2. Explicit `data-theme` attribute on `<html>`.
 *  3. The *rendered* page background — sampled from `--background`.
 *     This covers hosts where "light" is the absence of a class
 *     (e.g. Storybook's `withThemeByClassName({ light: '', dark:
 *     'dark' })`): without this step the hook would fall through to
 *     the system preference and report `dark` for a light page on a
 *     dark OS.
 *  4. System `prefers-color-scheme` — last resort, only when no theme
 *     tokens have been applied yet.
 *
 * For full theme control (setTheme, toggleTheme), use useThemeContext.
 *
 * @example
 * const theme = useResolvedTheme(); // 'light' | 'dark'
 */
export const useResolvedTheme = (): ResolvedTheme => {
  const [theme, setTheme] = useState<ResolvedTheme>('light');

  useEffect(() => {
    const sampleBackground = (): ResolvedTheme | null => {
      const probe = document.createElement('div');
      probe.style.cssText =
        'background-color:var(--background);position:absolute;width:0;height:0;pointer-events:none;';
      document.body.appendChild(probe);
      const rgb = getComputedStyle(probe).backgroundColor;
      probe.remove();

      const match = rgb.match(/\d+(\.\d+)?/g);
      if (!match || match.length < 3) return null;
      const [r, g, b] = match.map(Number) as [number, number, number];
      // Perceived luminance (ITU-R BT.601).
      const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
      return luminance > 0.5 ? 'light' : 'dark';
    };

    const checkTheme = (): ResolvedTheme => {
      const root = document.documentElement;

      if (root.classList.contains('dark')) return 'dark';
      if (root.classList.contains('light')) return 'light';

      const dataTheme = root.getAttribute('data-theme');
      if (dataTheme === 'dark') return 'dark';
      if (dataTheme === 'light') return 'light';

      // No explicit theme class/attr — infer from the painted surface.
      const sampled = sampleBackground();
      if (sampled) return sampled;

      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
      }
      return 'light';
    };

    setTheme(checkTheme());

    const observer = new MutationObserver(() => {
      setTheme(checkTheme());
    });
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class', 'data-theme', 'style'],
    });

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleMediaChange = () => setTheme(checkTheme());
    mediaQuery.addEventListener('change', handleMediaChange);

    return () => {
      observer.disconnect();
      mediaQuery.removeEventListener('change', handleMediaChange);
    };
  }, []);

  return theme;
};

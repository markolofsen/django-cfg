/**
 * ForceTheme - Force a specific theme for a section
 *
 * Wraps content to override the global theme setting.
 * Works by adding both the theme class and inline CSS variables
 * to ensure proper theme application regardless of parent context.
 */

'use client';

import React, { ReactNode } from 'react';

import { cn } from '../lib/utils';

interface ForceThemeProps {
  theme: 'light' | 'dark';
  children: ReactNode;
  className?: string;
}

/**
 * Token contract (ui-core Tailwind v4): base tokens are **full CSS colors**,
 * never bare HSL triplets. The utilities consume them raw — `.bg-muted {
 * background-color: var(--muted) }` — so `--muted: 0 0% 10%` (a triplet) is an
 * invalid color and the declaration is dropped (transparent fills, white
 * borders). Every value here is therefore wrapped in `hsl(...)`. The separate
 * `--color-*` block is intentionally gone: ui-core's `@theme inline` already
 * maps `--color-X: var(--X)`, so re-declaring it here is redundant and was the
 * only reason this component half-worked before. See ui-core styles README
 * §"Token format".
 */
const darkThemeVars = {
  '--background': 'hsl(0 0% 4%)',
  '--foreground': 'hsl(0 0% 98%)',
  '--card': 'hsl(0 0% 8%)',
  '--card-foreground': 'hsl(0 0% 98%)',
  '--popover': 'hsl(0 0% 12%)',
  '--popover-foreground': 'hsl(0 0% 98%)',
  '--primary': 'hsl(217 91% 60%)',
  '--primary-foreground': 'hsl(0 0% 100%)',
  '--secondary': 'hsl(0 0% 98%)',
  '--secondary-foreground': 'hsl(0 0% 9%)',
  '--muted': 'hsl(0 0% 10%)',
  '--muted-foreground': 'hsl(0 0% 60%)',
  '--accent': 'hsl(0 0% 15%)',
  '--accent-foreground': 'hsl(0 0% 98%)',
  '--destructive': 'hsl(0 84% 60%)',
  '--destructive-foreground': 'hsl(0 0% 98%)',
  '--border': 'hsl(0 0% 15%)',
  '--input': 'hsl(0 0% 15%)',
  '--ring': 'hsl(217 91% 60%)',
} as React.CSSProperties;

const lightThemeVars = {
  '--background': 'hsl(0 0% 96%)',
  '--foreground': 'hsl(0 0% 9%)',
  '--card': 'hsl(0 0% 100%)',
  '--card-foreground': 'hsl(0 0% 9%)',
  '--popover': 'hsl(0 0% 100%)',
  '--popover-foreground': 'hsl(0 0% 9%)',
  '--primary': 'hsl(217 91% 60%)',
  '--primary-foreground': 'hsl(0 0% 100%)',
  '--secondary': 'hsl(0 0% 9%)',
  '--secondary-foreground': 'hsl(0 0% 98%)',
  '--muted': 'hsl(0 0% 96%)',
  '--muted-foreground': 'hsl(0 0% 40%)',
  '--accent': 'hsl(0 0% 92%)',
  '--accent-foreground': 'hsl(0 0% 9%)',
  '--destructive': 'hsl(0 84% 60%)',
  '--destructive-foreground': 'hsl(0 0% 98%)',
  '--border': 'hsl(0 0% 90%)',
  '--input': 'hsl(0 0% 90%)',
  '--ring': 'hsl(217 91% 60%)',
} as React.CSSProperties;

export function ForceTheme({ theme, children, className }: ForceThemeProps) {
  const themeVars = theme === 'dark' ? darkThemeVars : lightThemeVars;

  return (
    <div
      className={cn(theme, className)}
      style={themeVars}
    >
      {children}
    </div>
  );
}

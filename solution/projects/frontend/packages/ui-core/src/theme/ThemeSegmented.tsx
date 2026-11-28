'use client';

/**
 * ThemeSegmented — a 3-way System / Light / Dark segmented control
 * (Claude / macOS settings style), as opposed to the binary `ThemeToggle`.
 *
 * Reads/writes the full theme via `useThemeContext` (`theme` + `setTheme`,
 * which support `'system'`). Must be used within ThemeProvider. SSR-safe:
 * renders a stable placeholder until mounted to avoid hydration mismatch.
 */

import { Monitor, Moon, Sun } from 'lucide-react';
import { useEffect, useState } from 'react';

import { cn } from '../lib/utils';
import { useThemeContext, type Theme } from './ThemeProvider';

export interface ThemeSegmentedProps {
  className?: string;
  /** Compact paddings for tight rows. */
  size?: 'default' | 'compact';
}

const OPTIONS: Array<{ value: Theme; icon: React.ComponentType<{ className?: string }>; label: string }> = [
  { value: 'system', icon: Monitor, label: 'System' },
  { value: 'light', icon: Sun, label: 'Light' },
  { value: 'dark', icon: Moon, label: 'Dark' },
];

export function ThemeSegmented({ className, size = 'default' }: ThemeSegmentedProps) {
  const { theme, setTheme } = useThemeContext();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const active: Theme = mounted ? (theme ?? 'system') : 'system';
  const btn = size === 'compact' ? 'h-7 w-7' : 'h-8 w-8';
  const icon = size === 'compact' ? 'size-3.5' : 'size-4';

  return (
    <div
      role="radiogroup"
      aria-label="Theme"
      className={cn(
        'rounded-control inline-flex items-center gap-0.5 border border-border bg-muted p-0.5',
        className,
      )}
    >
      {OPTIONS.map(({ value, icon: Icon, label }) => {
        const selected = active === value;
        return (
          <button
            key={value}
            type="button"
            role="radio"
            aria-checked={selected}
            aria-label={label}
            title={label}
            onClick={() => setTheme(value)}
            className={cn(
              'inline-flex items-center justify-center rounded-[calc(var(--radius-control)-0.25rem)] transition-colors',
              btn,
              selected
                ? 'bg-background text-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground',
            )}
          >
            <Icon className={icon} />
          </button>
        );
      })}
    </div>
  );
}

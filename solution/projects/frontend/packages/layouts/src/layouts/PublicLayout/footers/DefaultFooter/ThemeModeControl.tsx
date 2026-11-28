'use client';

import { Laptop, Moon, Sun } from 'lucide-react';
import React, { useEffect, useState } from 'react';

import { Button } from '@djangocfg/ui-core/components';
import { useForcedTheme, useThemeContext } from '@djangocfg/ui-core/theme';

interface ThemeModeControlProps {
  /** What to do when the route forces a theme via `ThemeOverride`. */
  lockedBehavior?: 'disable' | 'hide';
  /** Tooltip shown when locked. */
  lockedTitle?: string;
}

export function ThemeModeControl({
  lockedBehavior = 'disable',
  lockedTitle = 'Theme is set for this page',
}: ThemeModeControlProps) {
  const { theme, setTheme } = useThemeContext();
  const forcedTheme = useForcedTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const isLocked = Boolean(forcedTheme);
  // When locked, the active item reflects the forced theme — not the user's pick.
  const currentTheme: 'system' | 'light' | 'dark' = isLocked
    ? forcedTheme!
    : mounted
      ? ((theme as 'system' | 'light' | 'dark' | undefined) || 'system')
      : 'system';

  // Prepare item descriptors above JSX — no inline conditionals in the tree.
  const items: Array<{
    key: 'system' | 'light' | 'dark';
    icon: typeof Laptop;
    label: string;
  }> = [
    { key: 'system', icon: Laptop, label: 'Use system theme' },
    { key: 'light',  icon: Sun,    label: 'Use light theme' },
    { key: 'dark',   icon: Moon,   label: 'Use dark theme' },
  ];

  const baseItemClass = 'h-8 w-8 rounded-full p-0 text-muted-foreground hover:text-foreground';
  const activeItemClass = 'bg-background/80 text-foreground shadow-sm';
  const lockedItemClass = 'cursor-not-allowed opacity-60 hover:text-muted-foreground';

  if (isLocked && lockedBehavior === 'hide') {
    return null;
  }

  const containerClass = [
    'inline-flex items-center gap-1 rounded-full border border-border/60 bg-muted/30 p-1',
    isLocked ? 'cursor-not-allowed' : '',
  ].filter(Boolean).join(' ');
  const containerTitle = isLocked ? lockedTitle : undefined;

  return (
    <div className={containerClass} title={containerTitle} aria-disabled={isLocked}>
      {items.map((item) => {
        const Icon = item.icon;
        const isActive = currentTheme === item.key;
        const className = [
          baseItemClass,
          isActive ? activeItemClass : '',
          isLocked ? lockedItemClass : '',
        ].filter(Boolean).join(' ');
        const handleClick = isLocked ? undefined : () => setTheme(item.key);
        return (
          <Button
            key={item.key}
            type="button"
            variant="ghost"
            size="icon"
            className={className}
            onClick={handleClick}
            disabled={isLocked}
            aria-label={item.label}
            title={isLocked ? lockedTitle : item.label}
          >
            <Icon className="h-4 w-4" />
          </Button>
        );
      })}
    </div>
  );
}

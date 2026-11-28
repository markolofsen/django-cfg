'use client';

import { Laptop, Moon, Sun } from 'lucide-react';
import React, { useEffect, useState } from 'react';

import { Button } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { useThemeContext } from '@djangocfg/ui-core/theme';

import { LocaleSwitcher } from '../../_components/LocaleSwitcher';
import { useLayoutI18nOptional } from '../../../shared/LayoutI18nProvider';

export interface NavControlsProps {
  /** Show the theme (light / system / dark) pill. @default false */
  showThemeSwitcher?: boolean;
  /** Show the locale dropdown. Requires `i18n`. @default false */
  showLocaleSwitcher?: boolean;
  /** Visual size. `compact` matches navbar row, `default` matches footer. @default 'compact' */
  size?: 'compact' | 'default';
  /** Extra classes for the outer container. */
  className?: string;
}

function ThemeModeControl({ size }: { size: 'compact' | 'default' }) {
  const { theme, setTheme } = useThemeContext();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const currentTheme = mounted ? (theme || 'system') : 'system';
  const isActive = (value: 'system' | 'light' | 'dark') => currentTheme === value;

  const btnSize = size === 'compact' ? 'h-7 w-7' : 'h-8 w-8';
  const iconSize = size === 'compact' ? 'h-3.5 w-3.5' : 'h-4 w-4';
  const baseItemClass = `${btnSize} rounded-full p-0 text-muted-foreground hover:text-foreground`;
  const activeItemClass = 'bg-background/80 text-foreground shadow-sm';

  return (
    <div className="inline-flex items-center gap-0.5 rounded-[var(--radius-popover)] border border-border/60 bg-muted/30 p-0.5">
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className={cn(baseItemClass, isActive('system') && activeItemClass)}
        onClick={() => setTheme('system')}
        aria-label="Use system theme"
      >
        <Laptop className={iconSize} />
      </Button>
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className={cn(baseItemClass, isActive('light') && activeItemClass)}
        onClick={() => setTheme('light')}
        aria-label="Use light theme"
      >
        <Sun className={iconSize} />
      </Button>
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className={cn(baseItemClass, isActive('dark') && activeItemClass)}
        onClick={() => setTheme('dark')}
        aria-label="Use dark theme"
      >
        <Moon className={iconSize} />
      </Button>
    </div>
  );
}

/**
 * Navbar-sized theme + locale controls. Mirrors `DefaultFooter` controls but
 * tuned for a navbar row. Rendered by `NavActions` when `controls` are passed
 * to a navbar config.
 */
export function NavControls({
  showThemeSwitcher = false,
  showLocaleSwitcher = false,
  size = 'compact',
  className,
}: NavControlsProps) {
  const i18n = useLayoutI18nOptional();
  const renderLocale = showLocaleSwitcher && Boolean(i18n);
  if (!showThemeSwitcher && !renderLocale) return null;

  const localeBtnClass =
    size === 'compact'
      ? 'h-8 rounded-full border-border/60 bg-muted/30 px-2.5 text-xs hover:bg-muted/40'
      : 'h-9 rounded-full border-border/60 bg-muted/30 text-sm hover:bg-muted/40';

  return (
    <div className={cn('inline-flex items-center gap-1.5', className)}>
      {showThemeSwitcher && <ThemeModeControl size={size} />}
      {renderLocale && (
        <LocaleSwitcher
          // Navbars use the compact dropdown list (not the fullscreen dialog) —
          // a popover menu fits a dense top bar far better than a modal.
          variant="dropdown"
          buttonVariant="outline"
          size={size === 'compact' ? 'sm' : 'default'}
          showTriggerLabel={false}
          className={localeBtnClass}
        />
      )}
    </div>
  );
}

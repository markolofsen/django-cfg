/**
 * ThemeToggle - Theme switcher component
 *
 * Switches between light and dark themes.
 * Must be used within ThemeProvider.
 *
 * @example
 * ```tsx
 * import { ThemeToggle } from '@djangocfg/ui-core/theme';
 *
 * // Default
 * <ThemeToggle />
 *
 * // Compact (for mobile/tight spaces)
 * <ThemeToggle size="compact" />
 *
 * // Custom className
 * <ThemeToggle className="ml-auto" />
 * ```
 */

'use client';

import { Moon, Sun } from 'lucide-react';
import { useEffect, useState } from 'react';

import { Button } from '../components/forms/button';
import { useIsMobile } from '../hooks/media/useMobile';
import { cn } from '../lib/utils';
import { useForcedTheme } from './ForcedThemeContext';
import { useThemeContext } from './ThemeProvider';

export type ThemeLockBehavior = 'disable' | 'hide';

export interface ThemeToggleProps {
  /** Custom className */
  className?: string;
  /** Size variant (auto-detects mobile if not specified) */
  size?: 'default' | 'compact' | 'auto';
  /**
   * What to do when the current route forces a theme via `ThemeOverride`.
   * - `disable` (default): render the toggle disabled with a tooltip.
   * - `hide`: render nothing.
   */
  lockedBehavior?: ThemeLockBehavior;
  /** Title shown when the control is locked. */
  lockedTitle?: string;
}

export function ThemeToggle({
  className,
  size = 'auto',
  lockedBehavior = 'disable',
  lockedTitle = 'Theme is set for this page',
}: ThemeToggleProps) {
  const { resolvedTheme, toggleTheme } = useThemeContext();
  const forcedTheme = useForcedTheme();
  const [mounted, setMounted] = useState(false);
  const isMobile = useIsMobile();

  // Prevent hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  const isLocked = Boolean(forcedTheme);
  // Determine actual size based on prop and screen size
  const actualSize = size === 'auto' ? (isMobile ? 'compact' : 'default') : size;
  const buttonSize = actualSize === 'compact' ? 'h-8 w-8' : 'h-9 w-9';
  const iconSize = actualSize === 'compact' ? 'h-3.5 w-3.5' : 'h-4 w-4';

  // The icon always reflects what's on screen (forced or not) — that is
  // `resolvedTheme`. When locked, it shows the forced theme's icon.
  const showSun = mounted ? resolvedTheme === 'light' : true;

  if (isLocked && lockedBehavior === 'hide') {
    return null;
  }

  if (!mounted) {
    return (
      <Button
        variant="ghost"
        size="icon"
        className={cn(buttonSize, className)}
        disabled
      >
        <Sun className={iconSize} />
        <span className="sr-only">Toggle theme</span>
      </Button>
    );
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={isLocked ? undefined : toggleTheme}
      disabled={isLocked}
      title={isLocked ? lockedTitle : undefined}
      aria-label={isLocked ? lockedTitle : 'Toggle theme'}
      className={cn(buttonSize, isLocked && 'cursor-not-allowed opacity-60', className)}
    >
      {showSun ? <Sun className={iconSize} /> : <Moon className={iconSize} />}
      <span className="sr-only">{isLocked ? lockedTitle : 'Toggle theme'}</span>
    </Button>
  );
}

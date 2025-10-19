/**
 * ThemeToggle - Theme switcher component
 *
 * Switches between light and dark themes by toggling the 'dark' class on the html element.
 * Uses localStorage to persist the user's theme preference.
 *
 * @example
 * ```tsx
 * import { ThemeToggle } from '@djangocfg/ui';
 *
 * <ThemeToggle />
 * ```
 */

import { useEffect, useState } from 'react';
import { Moon, Sun } from 'lucide-react';
import { Button } from '../components/button';
import { useThemeContext } from './ThemeProvider';

export function ThemeToggle() {
  const { theme, toggleTheme } = useThemeContext();
  const [isMounted, setIsMounted] = useState(false);

  // Prevent hydration mismatch by only rendering after mount
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Don't render anything during SSR
  if (!isMounted) {
    return null;
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggleTheme}
      className="h-9 w-9"
      title={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
    >
      {theme === 'light' ? (
        <Sun className="h-4 w-4" />
      ) : (
        <Moon className="h-4 w-4" />
      )}
      <span className="sr-only">Toggle theme</span>
    </Button>
  );
}

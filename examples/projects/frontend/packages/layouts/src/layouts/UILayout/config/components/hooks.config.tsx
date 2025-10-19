/**
 * Hooks Configuration
 */

import React from 'react';
import type { ComponentConfig } from './types';

export const HOOKS: ComponentConfig[] = [
  {
    name: 'useMediaQuery',
    category: 'hooks',
    description: 'Responsive media query hook',
    importPath: "import { useMediaQuery } from '@djangocfg/ui';",
    example: `const isMobile = useMediaQuery('(max-width: 768px)');
const isDesktop = useMediaQuery('(min-width: 1024px)');

return isMobile ? <MobileView /> : <DesktopView />;`,
    preview: (
      <div className="p-4 border rounded-md">
        <code className="text-sm">
          useMediaQuery('(max-width: 768px)')
        </code>
        <p className="mt-2 text-sm text-muted-foreground">
          Returns boolean based on media query match
        </p>
      </div>
    ),
  },
  {
    name: 'useTheme',
    category: 'hooks',
    description: 'Theme management hook',
    importPath: "import { useTheme } from '@djangocfg/ui';",
    example: `const theme = useTheme(); // Returns 'light' | 'dark'

// Toggle theme manually
document.documentElement.classList.toggle('dark');`,
    preview: (
      <div className="p-4 border rounded-md">
        <code className="text-sm">
          const theme = useTheme();
        </code>
        <p className="mt-2 text-sm text-muted-foreground">
          Returns current theme: 'light' | 'dark'
        </p>
      </div>
    ),
  },
  {
    name: 'useCopy',
    category: 'hooks',
    description: 'Copy to clipboard hook',
    importPath: "import { useCopy } from '@djangocfg/ui';",
    example: `const { copyToClipboard } = useCopy();
const [copied, setCopied] = useState(false);

const handleCopy = async () => {
  await copyToClipboard('text to copy');
  setCopied(true);
};`,
    preview: (
      <div className="p-4 border rounded-md">
        <code className="text-sm">
          copyToClipboard(text)
        </code>
        <p className="mt-2 text-sm text-muted-foreground">
          Copy text to clipboard programmatically
        </p>
      </div>
    ),
  },
  {
    name: 'useCountdown',
    category: 'hooks',
    description: 'Countdown timer hook',
    importPath: "import { useCountdown } from '@djangocfg/ui';",
    example: `const targetDate = new Date('2025-12-31').toISOString();
const countdown = useCountdown(targetDate);

// Returns: { days, hours, minutes, seconds, isExpired }`,
    preview: (
      <div className="p-4 border rounded-md">
        <code className="text-sm">
          useCountdown(isoDateString)
        </code>
        <p className="mt-2 text-sm text-muted-foreground">
          Returns countdown object with days, hours, minutes, seconds
        </p>
      </div>
    ),
  },
  {
    name: 'useDebounce',
    category: 'hooks',
    description: 'Debounce value changes',
    importPath: "import { useDebounce } from '@djangocfg/ui';",
    example: `const [search, setSearch] = useState('');
const debouncedSearch = useDebounce(search, 500);

// debouncedSearch updates 500ms after last change`,
    preview: (
      <div className="p-4 border rounded-md">
        <code className="text-sm">
          useDebounce(value, delay)
        </code>
        <p className="mt-2 text-sm text-muted-foreground">
          Debounces value changes with specified delay
        </p>
      </div>
    ),
  },
  {
    name: 'useIsMobile',
    category: 'hooks',
    description: 'Check if device is mobile',
    importPath: "import { useIsMobile } from '@djangocfg/ui';",
    example: `const isMobile = useIsMobile(); // Boolean

return isMobile ? <MobileMenu /> : <DesktopMenu />;`,
    preview: (
      <div className="p-4 border rounded-md">
        <code className="text-sm">
          const isMobile = useIsMobile();
        </code>
        <p className="mt-2 text-sm text-muted-foreground">
          Returns true if viewport width {'<'} 768px
        </p>
      </div>
    ),
  },
];

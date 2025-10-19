import { useEffect, useState } from 'react';

export type Theme = 'light' | 'dark';

/**
 * Hook to detect and track the current theme
 * Supports both manual theme switching and system preference
 */
export const useTheme = (): Theme => {
  const [theme, setTheme] = useState<Theme>('light');
  
  useEffect(() => {
    const checkTheme = (): Theme => {
      // Check if dark class is applied to html element (manual theme)
      if (document.documentElement.classList.contains('dark')) {
        return 'dark';
      }
      
      // Check system preference
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
      }
      
      return 'light';
    };
    
    // Set initial theme
    setTheme(checkTheme());
    
    // Listen for manual theme changes (class changes on html element)
    const observer = new MutationObserver(() => {
      setTheme(checkTheme());
    });
    
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class']
    });
    
    // Listen for system theme changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleMediaChange = () => {
      setTheme(checkTheme());
    };
    
    mediaQuery.addEventListener('change', handleMediaChange);
    
    return () => {
      observer.disconnect();
      mediaQuery.removeEventListener('change', handleMediaChange);
    };
  }, []);
  
  return theme;
};

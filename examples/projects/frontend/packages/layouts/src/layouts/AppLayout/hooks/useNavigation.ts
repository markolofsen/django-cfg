/**
 * useNavigation Hook
 *
 * Navigation utilities
 */

import { useRouter } from 'next/router';
import { useAppContext } from '../context';

export interface UseNavigationReturn {
  /** Current pathname */
  currentPath: string;

  /** Check if path is active */
  isActive: (path: string) => boolean;

  /** Get page title for current route */
  getPageTitle: () => string;
}

/**
 * Navigation utilities hook
 *
 * @example
 * ```tsx
 * const { isActive, getPageTitle } = useNavigation();
 * const title = getPageTitle();
 * ```
 */
export function useNavigation(): UseNavigationReturn {
  const router = useRouter();
  const { routes, currentPath } = useAppContext();

  const isActive = (path: string): boolean => {
    if (currentPath === path) return true;
    if (path !== '/' && currentPath.startsWith(path)) return true;
    return false;
  };

  const getPageTitle = (): string => {
    return routes.getPageTitle(currentPath);
  };

  return {
    currentPath,
    isActive,
    getPageTitle,
  };
}

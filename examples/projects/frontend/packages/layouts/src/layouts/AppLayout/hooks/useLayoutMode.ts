/**
 * useLayoutMode Hook
 *
 * Returns current layout mode
 */

import { useAppContext } from '../context';
import type { LayoutMode } from '../types';

/**
 * Get current layout mode
 *
 * @returns Current layout mode ('public' | 'private' | 'auth')
 *
 * @example
 * ```tsx
 * const mode = useLayoutMode();
 * if (mode === 'private') {
 *   return <DashboardContent />;
 * }
 * ```
 */
export function useLayoutMode(): LayoutMode {
  const { layoutMode } = useAppContext();
  return layoutMode;
}

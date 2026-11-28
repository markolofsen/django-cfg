'use client';

import { useEffect } from 'react';

import { useRouteProgress } from '../provider/context';
import type { NavigationBehavior } from './store';

/**
 * Declare navigation behaviour for as long as the calling component is mounted:
 *
 * ```tsx
 * function Board() {
 *   useNavigationBehavior({ scroll: false, progress: false });
 * }
 * ```
 *
 * Needs a `RouteProgressProvider` above (BaseApp mounts one); without it this does nothing.
 */
export function useNavigationBehavior({ scroll, progress }: NavigationBehavior): void {
  const ctx = useRouteProgress();
  const behavior = ctx?.behavior;
  useEffect(() => behavior?.acquire({ scroll, progress }), [behavior, scroll, progress]);
}

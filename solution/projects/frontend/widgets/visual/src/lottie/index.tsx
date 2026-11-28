/**
 * LottiePlayer - Dynamic Import Wrapper
 *
 * Lazy loads the LottiePlayer component for optimal bundle size
 */

'use client';

import React, { lazy, Suspense } from 'react';
import { LottiePlayerProps } from './types';

// Lazy load the client component
const LottiePlayerClient = lazy(() =>
  import('./LottiePlayer.client').then((mod) => ({ default: mod.LottiePlayer }))
);

// Loading fallback component
const LoadingFallback = () => (
  <div className="flex items-center justify-center p-8" role="status" aria-live="polite">
    <div className="flex flex-col items-center gap-2">
      <div
        className="h-8 w-8 animate-spin rounded-full border-4 border-muted border-t-foreground motion-reduce:animate-[spin_1.5s_linear_infinite]"
        aria-hidden="true"
      />
      <span className="text-sm text-muted-foreground">Loading player...</span>
    </div>
  </div>
);

/**
 * LottiePlayer component wrapper with dynamic import
 *
 * This component automatically handles code splitting and lazy loading
 * of the Lottie player to optimize bundle size.
 *
 * Usage:
 * ```tsx
 * import { LottiePlayer } from '@djangocfg/ui-core/tools';
 *
 * <LottiePlayer
 *   src="https://example.com/animation.json"
 *   size="md"
 *   autoplay
 *   loop
 * />
 * ```
 */
export function LottiePlayer(props: LottiePlayerProps) {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <LottiePlayerClient {...props} />
    </Suspense>
  );
}

// Re-export types for convenience
export type {
  LottiePlayerProps,
  LottieSize,
  LottieSpeed,
  LottieDirection,
  LottieSegment,
} from './types';
export { useLottie } from './useLottie';
export type { UseLottieOptions, UseLottieReturn } from './useLottie';
export { usePrefersReducedMotion } from './usePrefersReducedMotion';

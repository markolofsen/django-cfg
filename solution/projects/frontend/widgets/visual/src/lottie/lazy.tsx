'use client';

/**
 * Lazy-loaded LottiePlayer Component
 *
 * Lottie library (~200KB) is loaded only when component is rendered.
 * Use this for automatic code-splitting with Suspense fallback.
 *
 * For direct imports without lazy loading, use:
 * import { LottiePlayer } from '@djangocfg/widget-visual/lottie-player'
 */

import { createLazyComponent } from '@djangocfg/widget-kit/lazy';
import type { LottiePlayerProps } from './types';

// ============================================================================
// Re-export types
// ============================================================================

export type {
  LottiePlayerProps,
  LottieSize,
  LottieSpeed,
  LottieDirection,
  LottieSegment,
} from './types';

// ============================================================================
// Lottie Loading Fallback
// ============================================================================

function LottieLoadingFallback() {
  return (
    <div
      className="flex items-center justify-center p-8"
      role="status"
      aria-live="polite"
    >
      <div className="flex flex-col items-center gap-2">
        <div
          className="h-8 w-8 animate-spin rounded-full border-4 border-muted border-t-primary motion-reduce:animate-[spin_1.5s_linear_infinite]"
          aria-hidden="true"
        />
        <span className="text-sm text-muted-foreground">Loading animation...</span>
      </div>
    </div>
  );
}

// ============================================================================
// Lazy Component
// ============================================================================

/**
 * LazyLottiePlayer - Lazy-loaded Lottie animation player
 *
 * Automatically shows loading state while Lottie loads (~200KB)
 */
export const LazyLottiePlayer = createLazyComponent<LottiePlayerProps>(
  () => import('./LottiePlayer.client').then((mod) => ({ default: mod.LottiePlayer })),
  {
    displayName: 'LazyLottiePlayer',
    fallback: <LottieLoadingFallback />,
  }
);

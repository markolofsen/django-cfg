/**
 * LottiePlayer Component
 *
 * Universal Lottie animation player component
 */

'use client';

import React from 'react';
import Lottie from 'react-lottie-player';

import { LottiePlayerProps } from './types';
import { useLottie } from './useLottie';
import { usePrefersReducedMotion } from './usePrefersReducedMotion';

// Size presets mapping
const SIZE_PRESETS = {
  xs: { width: 64, height: 64 },
  sm: { width: 128, height: 128 },
  md: { width: 256, height: 256 },
  lg: { width: 384, height: 384 },
  xl: { width: 512, height: 512 },
  full: { width: '100%', height: '100%' },
} as const;

const SPEED_STEPS = [0.5, 1, 1.5, 2] as const;

/**
 * LottiePlayer component for displaying Lottie animations
 *
 * Features:
 * - Loads animations from URLs or objects
 * - Size presets or custom dimensions
 * - Interactive playback controls (play/pause, loop, speed)
 * - Segment playback and hover-to-play
 * - Loading and error states
 * - Respects `prefers-reduced-motion`
 * - Event callbacks
 *
 * Usage:
 * ```tsx
 * // From URL with size preset
 * <LottiePlayer src="https://example.com/animation.json" size="md" autoplay loop />
 *
 * // Interactive controls
 * <LottiePlayer src={animationData} controls />
 *
 * // Play a frame range only
 * <LottiePlayer src={animationData} segment={[30, 90]} />
 *
 * // Play on hover
 * <LottiePlayer src={animationData} hoverToPlay autoplay={false} />
 * ```
 */
export function LottiePlayer({
  src,
  size = 'md',
  width,
  height,
  autoplay = true,
  loop = true,
  speed = 1,
  direction = 1,
  controls = false,
  segment,
  hoverToPlay = false,
  background,
  className,
  ariaLabel,
  respectReducedMotion = true,
  showLoading = true,
  onComplete,
  onLoad,
  onError,
}: LottiePlayerProps) {
  // Load animation data using our custom hook
  const { animationData, isLoading, error, retry } = useLottie({ src });
  const prefersReducedMotion = usePrefersReducedMotion();
  const reduceMotion = respectReducedMotion && prefersReducedMotion;

  // Interactive playback state (only used when `controls` is enabled).
  const [isPlaying, setIsPlaying] = React.useState(autoplay);
  const [loopEnabled, setLoopEnabled] = React.useState(Boolean(loop));
  const [currentSpeed, setCurrentSpeed] = React.useState<number>(speed);
  const [hovered, setHovered] = React.useState(false);

  // Keep internal state in sync if controlling props change.
  React.useEffect(() => setIsPlaying(autoplay), [autoplay]);
  React.useEffect(() => setLoopEnabled(Boolean(loop)), [loop]);
  React.useEffect(() => setCurrentSpeed(speed), [speed]);

  // Notify parent about load state once per loaded animation.
  const notifiedLoadRef = React.useRef<object | null>(null);
  React.useEffect(() => {
    if (animationData && notifiedLoadRef.current !== animationData) {
      notifiedLoadRef.current = animationData;
      onLoad?.();
    }
  }, [animationData, onLoad]);

  // Notify parent about errors once per error instance.
  const notifiedErrorRef = React.useRef<Error | null>(null);
  React.useEffect(() => {
    if (error && notifiedErrorRef.current !== error) {
      notifiedErrorRef.current = error;
      onError?.(error);
    }
    if (!error) {
      notifiedErrorRef.current = null;
    }
  }, [error, onError]);

  // Determine dimensions
  const dimensions = React.useMemo(() => {
    // Custom dimensions override size preset
    if (width !== undefined || height !== undefined) {
      return {
        width: width ?? SIZE_PRESETS[size].width,
        height: height ?? SIZE_PRESETS[size].height,
      };
    }
    return SIZE_PRESETS[size];
  }, [size, width, height]);

  // Handle complete event
  const handleComplete = React.useCallback(() => {
    // When not looping, reflect the finished state in the controls.
    if (!loopEnabled) {
      setIsPlaying(false);
    }
    onComplete?.();
  }, [loopEnabled, onComplete]);

  const togglePlay = React.useCallback(() => {
    setIsPlaying((prev) => !prev);
  }, []);

  const cycleSpeed = React.useCallback(() => {
    setCurrentSpeed((prev) => {
      const idx = SPEED_STEPS.indexOf(prev as (typeof SPEED_STEPS)[number]);
      // The modulo keeps the index in range (also when `prev` is unknown and idx is -1).
      return SPEED_STEPS[(idx + 1) % SPEED_STEPS.length] ?? prev;
    });
  }, []);

  // Resolve the effective play / loop / speed values.
  // Reduced motion forces a paused, non-looping static frame.
  const effectivePlaying = reduceMotion
    ? false
    : hoverToPlay
      ? hovered
      : controls
        ? isPlaying
        : autoplay;
  const effectiveLoop = reduceMotion ? false : controls ? loopEnabled : loop;
  const effectiveSpeed = controls ? currentSpeed : speed;

  // Segment playback: react-lottie-player expects [start, end].
  const segments = React.useMemo(
    () => (segment ? ([segment[0], segment[1]] as [number, number]) : undefined),
    [segment]
  );

  const containerStyle = React.useMemo<React.CSSProperties>(
    () => ({
      width: dimensions.width,
      height: dimensions.height,
      background: background || 'transparent',
    }),
    [dimensions.width, dimensions.height, background]
  );

  // Loading state
  if (isLoading && showLoading) {
    return (
      <div
        className={`flex items-center justify-center ${className || ''}`}
        style={containerStyle}
        role="status"
        aria-live="polite"
      >
        <div className="flex flex-col items-center gap-2">
          <div
            className="h-8 w-8 animate-spin rounded-full border-4 border-muted border-t-foreground motion-reduce:animate-[spin_1.5s_linear_infinite]"
            aria-hidden="true"
          />
          <span className="text-sm text-muted-foreground">Loading animation...</span>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div
        className={`flex items-center justify-center ${className || ''}`}
        style={containerStyle}
        role="alert"
      >
        <div className="flex flex-col items-center gap-2 p-4 text-center">
          <svg
            className="h-8 w-8 text-destructive"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <div className="text-sm text-destructive">{error.message}</div>
          <button
            type="button"
            onClick={retry}
            className="rounded bg-destructive/10 px-3 py-1 text-sm text-destructive transition-colors hover:bg-destructive/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // No animation data
  if (!animationData) {
    return null;
  }

  // Render the Lottie player
  return (
    <div
      className={className}
      role="img"
      aria-label={ariaLabel ?? 'Animation'}
      onMouseEnter={hoverToPlay ? () => setHovered(true) : undefined}
      onMouseLeave={hoverToPlay ? () => setHovered(false) : undefined}
    >
      <div style={containerStyle}>
        <Lottie
          animationData={animationData}
          play={effectivePlaying}
          loop={effectiveLoop}
          speed={effectiveSpeed}
          direction={direction}
          segments={segments}
          goTo={reduceMotion ? (segment ? segment[0] : 0) : undefined}
          style={{ width: '100%', height: '100%' }}
          onComplete={handleComplete}
          rendererSettings={{
            preserveAspectRatio: 'xMidYMid meet',
          }}
        />
      </div>
      {controls && (
        <div className="mt-2 flex items-center justify-center gap-1">
          <button
            type="button"
            onClick={togglePlay}
            disabled={reduceMotion}
            aria-label={effectivePlaying ? 'Pause animation' : 'Play animation'}
            aria-pressed={effectivePlaying}
            className="inline-flex h-7 w-7 items-center justify-center rounded text-foreground transition-colors hover:bg-muted disabled:opacity-40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            {effectivePlaying ? (
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <rect x="6" y="5" width="4" height="14" rx="1" />
                <rect x="14" y="5" width="4" height="14" rx="1" />
              </svg>
            ) : (
              <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M8 5v14l11-7z" />
              </svg>
            )}
          </button>
          <button
            type="button"
            onClick={() => setLoopEnabled((prev) => !prev)}
            aria-label={loopEnabled ? 'Disable loop' : 'Enable loop'}
            aria-pressed={loopEnabled}
            className={`inline-flex h-7 w-7 items-center justify-center rounded transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
              loopEnabled ? 'text-foreground' : 'text-muted-foreground'
            }`}
          >
            <svg
              className="h-4 w-4"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M17 1l4 4-4 4M3 11V9a4 4 0 014-4h14M7 23l-4-4 4-4M21 13v2a4 4 0 01-4 4H3"
              />
            </svg>
          </button>
          <button
            type="button"
            onClick={cycleSpeed}
            aria-label={`Playback speed ${currentSpeed}x, click to change`}
            className="inline-flex h-7 min-w-9 items-center justify-center rounded px-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            {currentSpeed}x
          </button>
          {reduceMotion && (
            <span className="ml-1 text-xs text-muted-foreground">Reduced motion</span>
          )}
        </div>
      )}
    </div>
  );
}

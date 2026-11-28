/**
 * LottiePlayer Types
 *
 * Type definitions for the Lottie animation player component
 */

export type LottieSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'full';

export type LottieSpeed = 0.5 | 1 | 1.5 | 2;

export type LottieDirection = 1 | -1;

/**
 * Inclusive [start, end] frame range for segment playback.
 */
export type LottieSegment = [number, number];

export interface LottiePlayerProps {
  /**
   * Animation data (JSON object) or URL to load from
   */
  src: string | object;

  /**
   * Size preset for the player
   * @default 'md'
   */
  size?: LottieSize;

  /**
   * Custom width (overrides size preset)
   */
  width?: number | string;

  /**
   * Custom height (overrides size preset)
   */
  height?: number | string;

  /**
   * Autoplay animation
   * @default true
   */
  autoplay?: boolean;

  /**
   * Loop animation
   * @default true
   */
  loop?: boolean | number;

  /**
   * Playback speed
   * @default 1
   */
  speed?: LottieSpeed;

  /**
   * Direction (1 = forward, -1 = reverse)
   * @default 1
   */
  direction?: LottieDirection;

  /**
   * Show interactive playback controls (play/pause, loop, speed)
   * @default false
   */
  controls?: boolean;

  /**
   * Play only a frame range, e.g. [30, 90]. Overrides full-clip playback.
   */
  segment?: LottieSegment;

  /**
   * Play the animation only while the pointer is over it. When the
   * pointer leaves, playback pauses. Ignored when `controls` drive playback.
   * @default false
   */
  hoverToPlay?: boolean;

  /**
   * Background color
   */
  background?: string;

  /**
   * CSS class name
   */
  className?: string;

  /**
   * Accessible label describing the animation for screen readers.
   */
  ariaLabel?: string;

  /**
   * Respect the user's `prefers-reduced-motion` setting. When the user
   * prefers reduced motion the animation renders a static first frame
   * instead of playing.
   * @default true
   */
  respectReducedMotion?: boolean;

  /**
   * Show loading state
   * @default true
   */
  showLoading?: boolean;

  /**
   * Callback when animation completes
   */
  onComplete?: () => void;

  /**
   * Callback when animation loads
   */
  onLoad?: () => void;

  /**
   * Callback on error
   */
  onError?: (error: Error) => void;
}

export interface LottieAnimationData {
  v: string;
  fr: number;
  ip: number;
  op: number;
  w: number;
  h: number;
  nm: string;
  ddd: number;
  // Opaque Lottie JSON: this package passes the document straight to the
  // player and never reads inside these.
  assets: unknown[];
  layers: unknown[];
}

/**
 * ImageViewer constants
 */

import type { ZoomPreset, ImageTransform } from '../types';

// =============================================================================
// SIZE LIMITS
// =============================================================================

/** Maximum image size before blocking (50MB) */
export const MAX_IMAGE_SIZE = 50 * 1024 * 1024;

/** Image size threshold for warning (10MB) */
export const WARNING_IMAGE_SIZE = 10 * 1024 * 1024;

/** Progressive loading threshold - use LQIP for images > 500KB */
export const PROGRESSIVE_LOADING_THRESHOLD = 500 * 1024;

// =============================================================================
// LQIP CONFIGURATION
// =============================================================================

/** Low-quality placeholder size (32x32) */
export const LQIP_SIZE = 32;

/** LQIP JPEG quality */
export const LQIP_QUALITY = 0.5;

// =============================================================================
// ZOOM CONFIGURATION
// =============================================================================

/** Minimum zoom level */
export const MIN_ZOOM = 0.1;

/** Maximum zoom level */
export const MAX_ZOOM = 8;

/** Pixels to pan per arrow-key press */
export const KEYBOARD_PAN_STEP = 60;

// =============================================================================
// GESTURE SENSITIVITY (macOS-grade pinch / trackpad zoom)
// =============================================================================
//
// react-zoom-pan-pinch computes the per-event wheel zoom magnitude as
// `smoothStep * |event.deltaY|` (its `smooth` path), which means the scale
// tracks the gesture 1:1 — a harder pinch / faster wheel moves more. The
// library default `smoothStep` is `0.001`, which on a macOS trackpad
// (whose pinch `deltaY` arrives as small ~±1–6 values with `ctrlKey=true`)
// produces ~0.005 scale/frame — imperceptible, the "weak pinch" symptom.
//
// We raise it so a natural trackpad pinch reaches a meaningful zoom in a
// single gesture while a mouse-wheel-with-ctrl notch (large |deltaY| ~100)
// stays a sensible discrete step. The library clamps to min/max scale, so
// the larger coefficient cannot overshoot the bounds.

/** Wheel/trackpad-pinch zoom sensitivity. scaleΔ = WHEEL_SMOOTH_STEP * |deltaY|. */
export const WHEEL_SMOOTH_STEP = 0.0055;

/** Touch pinch sensitivity (two-finger pinch on touchscreens). */
export const PINCH_STEP = 5;

/** Scale a double-click / double-tap zooms to, centred on the pointer. */
export const DOUBLE_CLICK_ZOOM = 2.5;

/** Within this of fit (scale 1) the image counts as "at rest". */
export const FIT_EPSILON = 0.02;

/** Idle delay (ms) before the lightbox chrome fades out when the pointer rests. */
export const CHROME_IDLE_MS = 2200;

/** Available zoom presets */
export const ZOOM_PRESETS: readonly ZoomPreset[] = [
  { label: 'Fit', value: 'fit' },
  { label: '25%', value: 0.25 },
  { label: '50%', value: 0.5 },
  { label: '100%', value: 1 },
  { label: '200%', value: 2 },
  { label: '400%', value: 4 },
] as const;

// =============================================================================
// DEFAULT VALUES
// =============================================================================

/** Default transform state */
export const DEFAULT_TRANSFORM: ImageTransform = {
  rotation: 0,
  flipH: false,
  flipV: false,
};

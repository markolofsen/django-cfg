/**
 * ImageViewer - Image viewer with zoom, pan, rotate, flip
 *
 * Features:
 * - Zoom with mouse wheel and presets (25%, 50%, 100%, 200%, 400%)
 * - Pan with drag
 * - Rotate 90°
 * - Flip horizontal/vertical
 * - Fullscreen dialog mode
 * - Keyboard shortcuts (+/-, 0 for reset, r for rotate)
 * - Progressive loading with LQIP for large images
 * - Checkerboard background for transparency
 * - Image dimensions display with caching
 */

// =============================================================================
// COMPONENTS
// =============================================================================

export { ImageViewer, ImageToolbar, ImageInfo } from './components';

// The lazy wrapper is what every caller here imports: the viewer carries
// react-zoom-pan-pinch, and no chat turn needs it until a reader opens a
// picture. Exported from the same entry so choosing it costs no extra subpath.
export { LazyImageViewer } from './lazy';

// The modal gallery (yet-another-react-lightbox). Prefer it to the `lightbox`
// presentation of `ImageViewer`; `LazyImageLightbox` defers the engine.
export { ImageLightbox, LazyImageLightbox } from './lightbox';

// =============================================================================
// HOOKS
// =============================================================================

export { useImageTransform, useImageLoading } from './hooks';
export type {
  UseImageTransformOptions,
  UseImageTransformReturn,
  UseImageLoadingOptions,
  UseImageLoadingReturn,
} from './hooks';

// =============================================================================
// TYPES
// =============================================================================

export type {
  ImageFile,
  ImageViewerProps,
  ImageLightboxProps,
  LightboxImage,
  ImageToolbarProps,
  ImageInfoProps,
  ImageTransform,
  ZoomPreset,
} from './types';

// =============================================================================
// UTILS
// =============================================================================

export {
  createLQIP,
  MAX_IMAGE_SIZE,
  WARNING_IMAGE_SIZE,
  PROGRESSIVE_LOADING_THRESHOLD,
  MIN_ZOOM,
  MAX_ZOOM,
  ZOOM_PRESETS,
  DEFAULT_TRANSFORM,
} from './utils';

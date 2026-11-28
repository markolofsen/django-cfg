/**
 * ImageViewer type definitions
 */

import type { MediaCopy } from '../i18n';

// =============================================================================
// FILE TYPES
// =============================================================================

export interface ImageFile {
  /** Display name for the image */
  name: string;
  /** File path used for change detection and caching */
  path: string;
  /** Optional MIME type */
  mimeType?: string;
}

export interface ImageItem {
  /** File info for this image */
  file: ImageFile;
  /** Direct image URL (use when serving from CDN/server) */
  src?: string;
  /**
   * Where the SAVE button reads its bytes, when that is not `src`.
   *
   * A browser honours `<a download>` only for a same-origin address; given a
   * foreign one it silently drops both the attribute and the filename and
   * navigates instead, so the picture opens in a tab. A host that can serve the
   * same bytes from its own origin supplies that address here.
   *
   * Absent means `src` is already savable — the ordinary case for a blob this
   * page hosts.
   */
  downloadSrc?: string;
  /** Raw image content — ArrayBuffer or base64/binary string (use when serving from memory) */
  content?: string | ArrayBuffer;
}

// =============================================================================
// COMPONENT PROPS
// =============================================================================

export interface ImageViewerProps {
  /**
   * Gallery images array.
   * When provided, enables gallery mode with prev/next navigation.
   * Single-image mode: pass one item.
   * Each item can have `src` (URL) or `content` (ArrayBuffer/base64) or both.
   */
  images: ImageItem[];
  /**
   * Initial index to show (default: 0).
   * Useful when opening a specific image from a grid.
   */
  initialIndex?: number;
  /** Hide expand button when already in dialog */
  inDialog?: boolean;
  /**
   * Render the restrained macOS-grade fullscreen lightbox chrome instead of
   * the embedded editing toolbar: a clean dark backdrop (no checkerboard),
   * idle-fading floating controls (close + prev/next + status pill), and no
   * rotate/flip slab. Intended for the click-to-expand image lightbox.
   * Implies `inDialog`.
   */
  lightbox?: boolean;
  /** Close request from the lightbox chrome (Esc / close button). */
  onRequestClose?: () => void;
  /**
   * Fraction of the viewport the image may occupy at rest, in the LIGHTBOX
   * presentation only (0 < fitScale ≤ 1). `1` (default) lets the image fill
   * edge-to-edge; `0.8` caps it at 80% so it opens with a comfortable margin
   * (Preview / Quick Look style) instead of slamming into the window edges.
   * Zoom / pan still operate from this fitted size. Ignored in the embedded
   * (non-lightbox) presentation.
   */
  fitScale?: number;
  /** Focus the viewer container on mount so its keyboard scope is active
   *  immediately (zoom/rotate/gallery hotkeys). Pair with `key={src}`
   *  upstream when the parent wants a fresh focus per source change. */
  autoFocus?: boolean;
  /**
   * Override any subset of the widget's English copy. Keys omitted fall back
   * to the defaults, so a host translating one label does not blank the rest.
   */
  copy?: Partial<MediaCopy>;
}

/** One slide of `ImageLightbox`: an address, never raw bytes. */
export interface LightboxImage {
  /** Image URL. */
  src: string;
  /** Shown as the alt text and used as the saved file's name. */
  name: string;
  /** Intrinsic size when known: lets the engine lay out before the bytes arrive. */
  width?: number;
  height?: number;
  /** Same-origin address the SAVE button reads (see `ImageItem.downloadSrc`). */
  downloadSrc?: string;
}

export interface ImageLightboxProps {
  images: LightboxImage[];
  /** Controlled visibility. */
  open: boolean;
  /** Slide on screen (default 0). */
  index?: number;
  /** Esc, backdrop click, pull-down or the close button. */
  onClose: () => void;
  onIndexChange?: (index: number) => void;
  /** Thumbnail strip for more than one image (default true). */
  thumbnails?: boolean;
  /** Override any subset of the widget's English copy. */
  copy?: Partial<MediaCopy>;
}

export interface ImageToolbarProps {
  /** Current zoom scale */
  scale: number;
  /** Current transform state */
  transform: ImageTransform;
  /** Rotate image callback */
  onRotate: () => void;
  /** Flip horizontal callback */
  onFlipH: () => void;
  /** Flip vertical callback */
  onFlipV: () => void;
  /** Zoom preset selection callback */
  onZoomPreset: (value: number | 'fit') => void;
  /** Expand to fullscreen callback (undefined hides button) */
  onExpand?: () => void;
  /**
   * Override any subset of the widget's English copy. Keys omitted fall back
   * to the defaults, so a host translating one label does not blank the rest.
   */
  copy?: Partial<MediaCopy>;
}

export interface ImageInfoProps {
  /** Image source URL */
  src: string;
}

// =============================================================================
// STATE TYPES
// =============================================================================

export interface ImageTransform {
  /** Rotation angle: 0, 90, 180, or 270 degrees */
  rotation: number;
  /** Horizontal flip state */
  flipH: boolean;
  /** Vertical flip state */
  flipV: boolean;
}

// =============================================================================
// UI TYPES
// =============================================================================

export interface ZoomPreset {
  /** Display label (e.g., "100%", "Fit") */
  label: string;
  /** Zoom value or 'fit' for fit-to-view */
  value: number | 'fit';
}

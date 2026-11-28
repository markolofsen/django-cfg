import type { ReactNode } from 'react'

/**
 * Media type for gallery items
 */
export type GalleryMediaType = 'image' | 'video'

/**
 * Single item in the gallery (image or video)
 */
export interface GalleryMediaItem {
  /** Unique identifier */
  id: string
  /** Full-size image/poster URL */
  src: string
  /** Thumbnail URL (optional, falls back to src) */
  thumbnail?: string
  /** Alt text for accessibility */
  alt?: string
  /** Image width (optional, for aspect ratio) */
  width?: number
  /** Image height (optional, for aspect ratio) */
  height?: number
  /** Media type (default: 'image') */
  type?: GalleryMediaType
  /** Video URL (required if type is 'video') */
  videoSrc?: string
  /** Video MIME type */
  videoType?: string
}

/**
 * Gallery state
 */
export interface GalleryState {
  /** Currently selected image index */
  currentIndex: number
  /** Whether lightbox is open */
  isLightboxOpen: boolean
  /** Whether image is zoomed in lightbox */
  isZoomed: boolean
  /** Whether current image is loading */
  isLoading: boolean
}

/**
 * Gallery actions
 */
export interface GalleryActions {
  /** Go to specific image by index */
  goTo: (index: number) => void
  /** Go to next image */
  next: () => void
  /** Go to previous image */
  prev: () => void
  /** Open lightbox at specific index */
  openLightbox: (index?: number) => void
  /** Close lightbox */
  closeLightbox: () => void
  /** Toggle zoom in lightbox */
  toggleZoom: () => void
  /** Set loading state */
  setLoading: (loading: boolean) => void
}

/**
 * Gallery context value
 */
export interface GalleryContextValue extends GalleryState, GalleryActions {
  /** All images in gallery */
  images: GalleryMediaItem[]
  /** Current image */
  currentImage: GalleryMediaItem | null
  /** Total number of images */
  total: number
  /** Whether there are multiple images */
  hasMultiple: boolean
}

/**
 * Preview mode for gallery
 */
export type GalleryPreviewMode = 'carousel' | 'grid'

/**
 * Props for Gallery component
 */
export interface GalleryProps {
  /** Array of images to display */
  images: GalleryMediaItem[]
  /** Initial image index */
  initialIndex?: number
  /** Preview mode: carousel (default) or grid */
  previewMode?: GalleryPreviewMode
  /** Number of images to show in grid preview (default: 5) */
  previewCount?: number
  /** Show thumbnail strip (carousel mode only) */
  showThumbnails?: boolean
  /** Show navigation controls (carousel mode only) */
  showControls?: boolean
  /** Show image counter */
  showCounter?: boolean
  /** Aspect ratio for main image (e.g., 16/9, 4/3) */
  aspectRatio?: number
  /** Enable lightbox on click */
  enableLightbox?: boolean
  /** Enable keyboard navigation */
  enableKeyboard?: boolean
  /** Callback when image changes */
  onImageChange?: (index: number, image: GalleryMediaItem) => void
  /** Callback when lightbox opens */
  onLightboxOpen?: () => void
  /** Callback when lightbox closes */
  onLightboxClose?: () => void
  /** Custom empty state */
  emptyState?: ReactNode
  /** Custom loading placeholder */
  loadingPlaceholder?: ReactNode
  /** Additional CSS class */
  className?: string
}

/**
 * Props for GalleryImage component
 */
export interface GalleryImageProps {
  /** Image data */
  image: GalleryMediaItem
  /** Whether to show loading skeleton */
  showLoading?: boolean
  /** On image load callback */
  onLoad?: () => void
  /** On image error callback */
  onError?: () => void
  /** On click callback */
  onClick?: () => void
  /** Priority loading */
  priority?: boolean
  /** Object fit mode: cover for thumbnails/grid, contain for lightbox */
  objectFit?: 'cover' | 'contain'
  /** Additional CSS class */
  className?: string
}

/**
 * Props for GalleryThumbnails component
 */
export interface GalleryThumbnailsProps {
  /** All images */
  images: GalleryMediaItem[]
  /** Currently selected index */
  currentIndex: number
  /** On thumbnail click */
  onSelect: (index: number) => void
  /** Thumbnail size */
  size?: 'sm' | 'md' | 'lg'
  /** Additional CSS class */
  className?: string
}

/**
 * Props for GalleryLightbox component
 */
export interface GalleryLightboxProps {
  /** Whether lightbox is open */
  open: boolean
  /** On close callback */
  onClose: () => void
  /** All images */
  images: GalleryMediaItem[]
  /** Current image index */
  currentIndex: number
  /** On index change */
  onIndexChange: (index: number) => void
  /** Show thumbnails in lightbox */
  showThumbnails?: boolean
  /** Enable zoom */
  enableZoom?: boolean
  /** Enable download button */
  enableDownload?: boolean
  /** Enable share button */
  enableShare?: boolean
  /** Title to display */
  title?: string
}

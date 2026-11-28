// Components
export {
  Gallery,
  GalleryCompact,
  GalleryGrid,
  GalleryImage,
  GalleryVideo,
  GalleryMedia,
  GalleryThumbnails,
  GalleryThumbnailsVirtual,
  GalleryLightbox,
} from './components'
export type { GalleryCompactProps, GalleryAspectRatio, GalleryGridProps, GalleryGridLayout } from './components'

// Hooks
export {
  useGallery,
  useSwipe,
  usePreloadImages,
  preloadImage,
  preloadImages,
  usePinchZoom,
  useVirtualList,
  useImageDimensions,
  clearDimensionsCache,
  getCachedDimensions,
} from './hooks'
export type {
  UseGalleryOptions,
  UseSwipeOptions,
  PinchZoomState,
  UsePinchZoomOptions,
  UsePinchZoomReturn,
  VirtualListOptions,
  VirtualListReturn,
  VirtualItem,
  ImageWithDimensions,
  UseImageDimensionsResult,
  UseImageDimensionsOptions,
} from './hooks'

// Utils
export {
  getOrientation,
  getAspectRatio,
  analyzeImage,
  analyzeImages,
} from './utils'
export type {
  ImageOrientation,
  AnalyzedImage,
} from './utils'

// Types
export type {
  GalleryMediaType,
  GalleryPreviewMode,
  GalleryMediaItem,
  GalleryState,
  GalleryActions,
  GalleryContextValue,
  GalleryProps,
  GalleryImageProps,
  GalleryThumbnailsProps,
  GalleryLightboxProps,
} from './types'

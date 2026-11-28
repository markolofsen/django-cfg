'use client'

import { memo, useCallback, useMemo } from 'react'
import { cn } from '@djangocfg/ui-core/lib'
import { Play } from 'lucide-react'
import { useImageLoadState } from '../../hooks/useImageLoadState'
import type { GalleryMediaItem } from '../../types'
import { normalizeImageUrl } from '../../utils'
import { ImageSpinner } from '../shared'

export type GalleryGridLayout =
  | 'auto'
  | 'single'
  | 'two-cols'
  | 'hero-left'
  | 'grid-2x2'
  | 'mosaic-5'

export interface GalleryGridProps {
  /** Array of images to display */
  images: GalleryMediaItem[]
  /** Maximum images to show in grid */
  maxVisible?: number
  /** Grid layout (auto picks based on count) */
  layout?: GalleryGridLayout
  /** Aspect ratio for the grid container */
  aspectRatio?: number
  /** Gap between grid items (tailwind spacing) */
  gap?: 1 | 2 | 3 | 4
  /** Border radius */
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | '2xl'
  /** Callback when image is clicked */
  onImageClick?: (index: number) => void
  /** Show "+N more" badge */
  showMoreBadge?: boolean
  /** Show loading skeleton */
  loading?: boolean
  /** Stagger delay between image reveals (ms), 0 to disable */
  staggerDelay?: number
  /** Additional CSS class */
  className?: string
}

const GAP_CLASSES = {
  1: 'gap-1',
  2: 'gap-2',
  3: 'gap-3',
  4: 'gap-4',
} as const

const ROUNDED_CLASSES = {
  none: 'rounded-none',
  sm: 'rounded-sm',
  md: 'rounded-md',
  lg: 'rounded-lg',
  xl: 'rounded-xl',
  '2xl': 'rounded-2xl',
} as const

/**
 * Get layout based on image count
 */
function getLayoutForCount(count: number): GalleryGridLayout {
  if (count === 1) return 'single'
  if (count === 2) return 'two-cols'
  if (count === 3) return 'hero-left'
  if (count === 4) return 'grid-2x2'
  return 'mosaic-5'
}

/**
 * GalleryGrid - Fixed layout grid for property images
 *
 * Airbnb-style layouts based on image count:
 * - 1 image: full width
 * - 2 images: side by side
 * - 3 images: hero left + 2 stacked right
 * - 4 images: 2x2 grid
 * - 5+ images: hero left + 2x2 grid right
 */
export const GalleryGrid = memo(function GalleryGrid({
  images,
  maxVisible = 5,
  layout = 'auto',
  aspectRatio = 16 / 9,
  gap = 2,
  rounded = 'xl',
  onImageClick,
  showMoreBadge = true,
  loading = false,
  staggerDelay = 75,
  className,
}: GalleryGridProps) {
  const visibleImages = useMemo(() => {
    return images.slice(0, maxVisible)
  }, [images, maxVisible])

  const currentLayout = useMemo((): GalleryGridLayout => {
    if (layout !== 'auto') return layout
    return getLayoutForCount(visibleImages.length || maxVisible)
  }, [layout, visibleImages.length, maxVisible])

  const remainingCount = useMemo(() => {
    return Math.max(0, images.length - maxVisible)
  }, [images.length, maxVisible])

  const handleClick = useCallback(
    (index: number) => {
      onImageClick?.(index)
    },
    [onImageClick]
  )

  // Show skeleton when loading or no images yet
  if (loading || images.length === 0) {
    return (
      <div
        className={cn(
          'relative overflow-hidden',
          ROUNDED_CLASSES[rounded],
          className
        )}
        style={{ aspectRatio }}
      >
        <div className="absolute inset-0">
          <GridSkeleton layout={currentLayout} gap={gap} />
        </div>
      </div>
    )
  }

  return (
    <div
      className={cn(
        'relative overflow-hidden',
        ROUNDED_CLASSES[rounded],
        className
      )}
      style={{ aspectRatio }}
    >
      <div className="absolute inset-0">
        <GridLayout
          layout={currentLayout}
          images={visibleImages}
          gap={gap}
          remainingCount={remainingCount}
          showMoreBadge={showMoreBadge}
          staggerDelay={staggerDelay}
          onImageClick={handleClick}
        />
      </div>
    </div>
  )
})

// Grid layout renderer
interface GridLayoutProps {
  layout: GalleryGridLayout
  images: GalleryMediaItem[]
  gap: 1 | 2 | 3 | 4
  remainingCount: number
  showMoreBadge: boolean
  staggerDelay: number
  onImageClick: (index: number) => void
}

const GridLayout = memo(function GridLayout({
  layout,
  images,
  gap,
  remainingCount,
  showMoreBadge,
  staggerDelay,
  onImageClick,
}: GridLayoutProps) {
  if (!images || images.length === 0) return null

  // Guarded non-empty above; bound once so every layout can index it safely.
  const firstImage = images[0]
  if (!firstImage) return null

  switch (layout) {
    case 'single':
      return (
        <GridItem
          image={firstImage}
          index={0}
          staggerDelay={staggerDelay}
          onClick={onImageClick}
          className="w-full h-full"
        />
      )

    case 'two-cols':
      return (
        <div className={cn('grid grid-cols-2 h-full', GAP_CLASSES[gap])}>
          {images.slice(0, 2).map((image, index) => (
            <GridItem
              key={image.id}
              image={image}
              index={index}
              staggerDelay={staggerDelay}
              onClick={onImageClick}
              showBadge={showMoreBadge && index === 1 && remainingCount > 0}
              badgeCount={remainingCount}
            />
          ))}
        </div>
      )

    case 'hero-left':
      return (
        <div
          className={cn('h-full', GAP_CLASSES[gap])}
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
          }}
        >
          <GridItem
            image={firstImage}
            index={0}
            staggerDelay={staggerDelay}
            onClick={onImageClick}
          />
          <div
            className={cn('h-full overflow-hidden', GAP_CLASSES[gap])}
            style={{
              display: 'grid',
              gridTemplateRows: '1fr 1fr',
            }}
          >
            {images.slice(1, 3).map((image, index) => (
              <GridItem
                key={image.id}
                image={image}
                index={index + 1}
                staggerDelay={staggerDelay}
                onClick={onImageClick}
                showBadge={showMoreBadge && index === 1 && remainingCount > 0}
                badgeCount={remainingCount}
              />
            ))}
          </div>
        </div>
      )

    case 'grid-2x2':
      return (
        <div className={cn('grid grid-cols-2 grid-rows-2 h-full', GAP_CLASSES[gap])}>
          {images.slice(0, 4).map((image, index) => (
            <GridItem
              key={image.id}
              image={image}
              index={index}
              staggerDelay={staggerDelay}
              onClick={onImageClick}
              showBadge={showMoreBadge && index === 3 && remainingCount > 0}
              badgeCount={remainingCount}
            />
          ))}
        </div>
      )

    case 'mosaic-5':
    default:
      // Airbnb-style: hero (50%) + 2x2 grid (50%) using single grid with areas
      return (
        <div
          className={cn('h-full', GAP_CLASSES[gap])}
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr 1fr 1fr',
            gridTemplateRows: '1fr 1fr',
            gridTemplateAreas: `
              "hero hero img2 img3"
              "hero hero img4 img5"
            `,
          }}
        >
          <GridItem
            image={firstImage}
            index={0}
            staggerDelay={staggerDelay}
            onClick={onImageClick}
            style={{ gridArea: 'hero' }}
          />
          {images[1] && (
            <GridItem
              key={images[1].id}
              image={images[1]}
              index={1}
              staggerDelay={staggerDelay}
              onClick={onImageClick}
              style={{ gridArea: 'img2' }}
            />
          )}
          {images[2] && (
            <GridItem
              key={images[2].id}
              image={images[2]}
              index={2}
              staggerDelay={staggerDelay}
              onClick={onImageClick}
              style={{ gridArea: 'img3' }}
            />
          )}
          {images[3] && (
            <GridItem
              key={images[3].id}
              image={images[3]}
              index={3}
              staggerDelay={staggerDelay}
              onClick={onImageClick}
              style={{ gridArea: 'img4' }}
            />
          )}
          {images[4] && (
            <GridItem
              key={images[4].id}
              image={images[4]}
              index={4}
              staggerDelay={staggerDelay}
              onClick={onImageClick}
              showBadge={showMoreBadge && remainingCount > 0}
              badgeCount={remainingCount}
              style={{ gridArea: 'img5' }}
            />
          )}
        </div>
      )
  }
})

// Single grid item
interface GridItemProps {
  image: GalleryMediaItem
  index: number
  staggerDelay: number
  onClick: (index: number) => void
  className?: string
  style?: React.CSSProperties
  showBadge?: boolean
  badgeCount?: number
}

const GridItem = memo(function GridItem({
  image,
  index,
  staggerDelay,
  onClick,
  className,
  style,
  showBadge = false,
  badgeCount = 0,
}: GridItemProps) {
  // Also reads the element's own `complete` state: an image that finished
  // before hydration never fires `onLoad` again. See the hook.
  const imageSrc = image?.thumbnail || image?.src
  const { ref: imgRef, isLoaded, hasError, onLoad: handleLoad, onError: handleError } =
    useImageLoadState(imageSrc)

  const handleClick = useCallback(() => {
    onClick(index)
  }, [onClick, index])

  // The first tile is the page's LCP. Hidden until `onLoad`, it cannot paint
  // before hydration however early the bytes arrive: Lighthouse put 2.2 s of
  // render delay on it (carapis.com, 2026-10-21). It shows as the browser
  // draws it; the fade and spinner stay for the lazy tiles.
  const isLead = index === 0

  if (!image) return null

  const isVideo = image.type === 'video'
  const animationDelay = staggerDelay > 0 ? `${index * staggerDelay}ms` : '0ms'

  return (
    <button
      type="button"
      className={cn(
        'relative overflow-hidden bg-muted h-full w-full min-w-0 min-h-0',
        'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-inset',
        'group',
        className
      )}
      style={style}
      onClick={handleClick}
      aria-label={`View image ${index + 1}`}
    >
      {/* Loading spinner - shows until image loads */}
      {!isLead && !isLoaded && !hasError && (
        <div className="absolute inset-0 flex items-center justify-center z-10">
          <ImageSpinner size="md" />
        </div>
      )}

      <img
        ref={imgRef}
        src={normalizeImageUrl(image.thumbnail || image.src)}
        alt={image.alt || `Image ${index + 1}`}
        className={cn(
          'w-full h-full object-cover transition-all duration-300 group-hover:scale-105',
          // Hide until loaded, then fade in
          !isLead && !isLoaded && 'opacity-0',
          (isLead || isLoaded) && 'opacity-100'
        )}
        style={staggerDelay > 0 && isLoaded ? { animationDelay } : undefined}
        loading={isLead ? 'eager' : 'lazy'}
        fetchPriority={isLead ? 'high' : 'auto'}
        onLoad={handleLoad}
        onError={handleError}
      />

      {/* Hover overlay */}
      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors" />

      {/* Video indicator */}
      {isVideo && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-12 h-12 rounded-full bg-black/60 flex items-center justify-center">
            <Play className="w-6 h-6 text-white ml-0.5" />
          </div>
        </div>
      )}

      {/* "+N more" badge */}
      {showBadge && badgeCount > 0 && (
        <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
          <span className="text-white text-xl font-semibold">
            +{badgeCount}
          </span>
        </div>
      )}
    </button>
  )
})

// Skeleton component matching grid layouts
interface GridSkeletonProps {
  layout: GalleryGridLayout
  gap: 1 | 2 | 3 | 4
}

const GridSkeleton = memo(function GridSkeleton({ layout, gap }: GridSkeletonProps) {
  const skeletonCell = "bg-muted animate-pulse"

  switch (layout) {
    case 'single':
      return <div className={cn('h-full w-full', skeletonCell)} />

    case 'two-cols':
      return (
        <div className={cn('grid grid-cols-2 h-full', GAP_CLASSES[gap])}>
          <div className={skeletonCell} />
          <div className={skeletonCell} />
        </div>
      )

    case 'hero-left':
      return (
        <div
          className={cn('h-full', GAP_CLASSES[gap])}
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
          }}
        >
          <div className={skeletonCell} />
          <div
            className={cn('h-full', GAP_CLASSES[gap])}
            style={{
              display: 'grid',
              gridTemplateRows: '1fr 1fr',
            }}
          >
            <div className={skeletonCell} />
            <div className={skeletonCell} />
          </div>
        </div>
      )

    case 'grid-2x2':
      return (
        <div className={cn('grid grid-cols-2 grid-rows-2 h-full', GAP_CLASSES[gap])}>
          <div className={skeletonCell} />
          <div className={skeletonCell} />
          <div className={skeletonCell} />
          <div className={skeletonCell} />
        </div>
      )

    case 'mosaic-5':
    default:
      return (
        <div
          className={cn('h-full', GAP_CLASSES[gap])}
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr 1fr 1fr',
            gridTemplateRows: '1fr 1fr',
            gridTemplateAreas: `
              "hero hero img2 img3"
              "hero hero img4 img5"
            `,
          }}
        >
          <div className={skeletonCell} style={{ gridArea: 'hero' }} />
          <div className={skeletonCell} style={{ gridArea: 'img2' }} />
          <div className={skeletonCell} style={{ gridArea: 'img3' }} />
          <div className={skeletonCell} style={{ gridArea: 'img4' }} />
          <div className={skeletonCell} style={{ gridArea: 'img5' }} />
        </div>
      )
  }
})

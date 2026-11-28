'use client'

import { memo, useCallback, useEffect, useMemo } from 'react'
import { cn } from '@djangocfg/ui-core/lib'
import { useImageLoadState } from '../../hooks/useImageLoadState'
import { useVirtualList } from '../../hooks/useVirtualList'
import type { GalleryThumbnailsProps } from '../../types'
import { normalizeImageUrl } from '../../utils'
import { ImageSpinner } from '../shared'

const SIZES = {
  sm: { width: 56, height: 40 },
  md: { width: 80, height: 56 },
  lg: { width: 96, height: 72 },
} as const

/**
 * GalleryThumbnailsVirtual - Virtualized thumbnail strip for large galleries
 * Only renders visible thumbnails + buffer for optimal performance
 */
export const GalleryThumbnailsVirtual = memo(function GalleryThumbnailsVirtual({
  images,
  currentIndex,
  onSelect,
  size = 'md',
  className,
}: GalleryThumbnailsProps) {
  const dimensions = SIZES[size]

  const { containerRef, totalWidth, virtualItems, scrollToIndex } = useVirtualList({
    itemCount: images.length,
    itemWidth: dimensions.width,
    gap: 8,
    overscan: 3,
  })

  // Scroll active thumbnail into view
  useEffect(() => {
    scrollToIndex(currentIndex)
  }, [currentIndex, scrollToIndex])

  // Handle thumbnail click
  const handleClick = useCallback(
    (index: number) => {
      onSelect(index)
    },
    [onSelect]
  )

  if (images.length <= 1) return null

  return (
    <div
      ref={containerRef}
      className={cn(
        'relative overflow-x-auto scrollbar-hide p-1',
        className
      )}
    >
      {/* Spacer for total scroll width */}
      <div style={{ width: totalWidth, height: dimensions.height }} className="relative">
        {virtualItems.map((virtualItem) => {
          const image = images[virtualItem.index]
          if (!image) return null
          const isActive = virtualItem.index === currentIndex

          return (
            <VirtualThumbnail
              key={image.id}
              image={image}
              index={virtualItem.index}
              isActive={isActive}
              left={virtualItem.start}
              width={dimensions.width}
              height={dimensions.height}
              onClick={handleClick}
            />
          )
        })}
      </div>
    </div>
  )
})

// Extracted virtual thumbnail component
interface VirtualThumbnailProps {
  image: { id: string; src: string; thumbnail?: string; alt?: string }
  index: number
  isActive: boolean
  left: number
  width: number
  height: number
  onClick: (index: number) => void
}

const VirtualThumbnail = memo(function VirtualThumbnail({
  image,
  index,
  isActive,
  left,
  width,
  height,
  onClick,
}: VirtualThumbnailProps) {
  // Also reads the element's own `complete` state: an image that finished
  // before hydration never fires `onLoad` again. See the hook.
  const imageSrc = useMemo(() => image?.thumbnail || image?.src, [image?.thumbnail, image?.src])
  const { ref: imgRef, isLoaded, onLoad: handleLoad } = useImageLoadState(imageSrc)

  const handleClick = useCallback(() => {
    onClick(index)
  }, [onClick, index])

  return (
    <button
      type="button"
      className={cn(
        'absolute top-0 rounded-lg overflow-hidden bg-muted',
        'border-2 transition-all duration-200',
        'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary',
        isActive
          ? 'border-primary ring-1 ring-primary/30'
          : 'border-transparent hover:border-muted-foreground/30'
      )}
      style={{
        left,
        width,
        height,
      }}
      onClick={handleClick}
      aria-label={`View image ${index + 1}`}
      aria-current={isActive ? 'true' : undefined}
    >
      {/* Loading spinner */}
      {!isLoaded && (
        <div className="absolute inset-0 flex items-center justify-center">
          <ImageSpinner size="sm" />
        </div>
      )}

      <img
        ref={imgRef}
        src={normalizeImageUrl(image.thumbnail || image.src)}
        alt={image.alt || `Thumbnail ${index + 1}`}
        className={cn(
          'w-full h-full object-cover transition-opacity duration-200',
          isLoaded ? 'opacity-100' : 'opacity-0'
        )}
        loading="lazy"
        onLoad={handleLoad}
      />

      {/* Active overlay */}
      {isActive && (
        <div className="absolute inset-0 bg-primary/10" />
      )}
    </button>
  )
})

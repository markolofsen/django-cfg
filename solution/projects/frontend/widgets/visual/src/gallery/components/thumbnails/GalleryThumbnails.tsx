'use client'

import { memo, useRef, useEffect, useCallback, Suspense, lazy, useMemo } from 'react'
import { cn } from '@djangocfg/ui-core/lib'
import { useImageLoadState } from '../../hooks/useImageLoadState'
import type { GalleryThumbnailsProps } from '../../types'
import { normalizeImageUrl } from '../../utils'
import { ImageSpinner } from '../shared'

// Lazy load virtualized thumbnails - only for 50+ images
const GalleryThumbnailsVirtual = lazy(() =>
  import('./GalleryThumbnailsVirtual').then((mod) => ({ default: mod.GalleryThumbnailsVirtual }))
)

const SIZES = {
  sm: 'w-14 h-10',
  md: 'w-20 h-14',
  lg: 'w-24 h-18',
} as const

/** Threshold for switching to virtualized rendering */
const VIRTUALIZATION_THRESHOLD = 50

/**
 * GalleryThumbnails - Horizontal scrollable thumbnail strip
 * Automatically switches to virtualized rendering for 50+ images
 */
export const GalleryThumbnails = memo(function GalleryThumbnails(props: GalleryThumbnailsProps) {
  const { images } = props

  // Use virtualized version for large galleries (lazy loaded)
  if (images.length >= VIRTUALIZATION_THRESHOLD) {
    return (
      <Suspense fallback={<ThumbnailsSkeleton className={props.className} />}>
        <GalleryThumbnailsVirtual {...props} />
      </Suspense>
    )
  }

  return <GalleryThumbnailsRegular {...props} />
})

// Simple skeleton for loading state
const ThumbnailsSkeleton = memo(function ThumbnailsSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn('flex gap-2 overflow-hidden p-1', className)}>
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="w-20 h-14 rounded-lg bg-muted animate-pulse flex-shrink-0" />
      ))}
    </div>
  )
})

/**
 * Regular (non-virtualized) thumbnails for smaller galleries
 */
const GalleryThumbnailsRegular = memo(function GalleryThumbnailsRegular({
  images,
  currentIndex,
  onSelect,
  size = 'md',
  className,
}: GalleryThumbnailsProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const itemRefs = useRef<(HTMLButtonElement | null)[]>([])

  // Scroll active thumbnail into view
  useEffect(() => {
    const activeItem = itemRefs.current[currentIndex]
    if (activeItem && containerRef.current) {
      const container = containerRef.current
      const itemLeft = activeItem.offsetLeft
      const itemWidth = activeItem.offsetWidth
      const containerWidth = container.offsetWidth
      const scrollLeft = container.scrollLeft

      // Check if item is not fully visible
      if (itemLeft < scrollLeft || itemLeft + itemWidth > scrollLeft + containerWidth) {
        activeItem.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest',
          inline: 'center',
        })
      }
    }
  }, [currentIndex])

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
        'flex gap-2 overflow-x-auto scrollbar-hide p-1',
        className
      )}
    >
      {images.map((image, index) => (
        <ThumbnailButton
          key={image.id}
          ref={(el) => {
            itemRefs.current[index] = el
          }}
          image={image}
          index={index}
          isActive={index === currentIndex}
          size={size}
          onClick={handleClick}
        />
      ))}
    </div>
  )
})

// Extracted thumbnail button component
interface ThumbnailButtonProps {
  image: { id: string; src: string; thumbnail?: string; alt?: string }
  index: number
  isActive: boolean
  size: 'sm' | 'md' | 'lg'
  onClick: (index: number) => void
}

const ThumbnailButton = memo(
  function ThumbnailButton({
    image,
    index,
    isActive,
    size,
    onClick,
    ref,
  }: ThumbnailButtonProps & { ref?: React.Ref<HTMLButtonElement> }) {
    // Also reads the element's own `complete` state: an image that finished
    // before hydration never fires `onLoad` again. See the hook.
    const imageSrc = useMemo(() => image?.thumbnail || image?.src, [image?.thumbnail, image?.src])
    const { ref: imgRef, isLoaded, onLoad: handleLoad } = useImageLoadState(imageSrc)

    const handleClick = useCallback(() => {
      onClick(index)
    }, [onClick, index])

    return (
      <button
        ref={ref}
        type="button"
        className={cn(
          'relative flex-shrink-0 rounded-lg overflow-hidden bg-muted',
          'border-2 transition-all duration-200',
          'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary',
          SIZES[size],
          isActive
            ? 'border-primary ring-1 ring-primary/30'
            : 'border-transparent hover:border-muted-foreground/30'
        )}
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
  }
)

'use client'

import { memo, useCallback, useEffect, useState, useMemo } from 'react'
import { cn } from '@djangocfg/ui-core/lib'
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  type CarouselApi,
} from '@djangocfg/ui-core/components'
import { ChevronLeft, ChevronRight, ImageOff } from 'lucide-react'
import { GalleryMedia } from '../media'
import type { GalleryMediaItem } from '../../types'

/** Preset aspect ratios for common use cases */
export type GalleryAspectRatio = '16/9' | '4/3' | '3/2' | '1/1' | 'auto'

export interface GalleryCompactProps {
  /** Array of images to display */
  images: GalleryMediaItem[]
  /** Aspect ratio preset or 'auto' to fill parent (default: 'auto') */
  aspectRatio?: GalleryAspectRatio
  /** Show dots indicator (default: true) */
  showDots?: boolean
  /** Max dots to show (default: 5) */
  maxDots?: number
  /** Show counter badge (default: false) */
  showCounter?: boolean
  /** Show navigation arrows on hover (default: true) */
  showArrows?: boolean
  /** Enable zoom effect on hover (default: true) */
  enableZoom?: boolean
  /** On image click callback */
  onClick?: () => void
  /** Additional CSS class */
  className?: string
}

/**
 * GalleryCompact - Minimal carousel for property/vehicle cards
 *
 * Features:
 * - Simple swipe carousel
 * - Dots indicator (mobile-style)
 * - Navigation arrows on hover (desktop)
 * - Hover zoom effect on images
 * - Lazy loading - only loads active image + neighbors
 * - Fills parent container
 * - Stops event propagation on navigation
 */
/** Map aspect ratio presets to CSS values */
const aspectRatioMap: Record<GalleryAspectRatio, string | undefined> = {
  '16/9': '16 / 9',
  '4/3': '4 / 3',
  '3/2': '3 / 2',
  '1/1': '1 / 1',
  'auto': undefined,
}

export const GalleryCompact = memo(function GalleryCompact({
  images,
  aspectRatio = 'auto',
  showDots = true,
  maxDots = 5,
  showCounter = false,
  showArrows = true,
  enableZoom = true,
  onClick,
  className,
}: GalleryCompactProps) {
  const [api, setApi] = useState<CarouselApi>()
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isHovered, setIsHovered] = useState(false)
  // Track if component is mounted (client-side) to avoid hydration mismatches
  const [isMounted, setIsMounted] = useState(false)

  // Compute aspect ratio style - if set, we control height via aspect-ratio, otherwise fill parent
  const aspectRatioStyle = aspectRatioMap[aspectRatio]
  const containerStyle = aspectRatioStyle ? { aspectRatio: aspectRatioStyle } : undefined
  const hasFixedAspect = aspectRatio !== 'auto'
  const containerClass = hasFixedAspect ? 'relative w-full overflow-hidden' : 'relative w-full h-full overflow-hidden'

  useEffect(() => {
    setIsMounted(true)
  }, [])

  const total = images.length
  const hasMultiple = total > 1
  const firstImage = images[0]
  // Stable key for carousel reset on images change
  const carouselKey = images[0]?.id ?? 'empty'

  // Determine which images should be loaded (current + neighbors for smooth transition)
  const loadedIndices = useMemo(() => {
    if (total === 0) return new Set<number>()
    const indices = new Set<number>()
    // Always load first image
    indices.add(0)
    // Load current
    indices.add(currentIndex)
    // Load neighbors for smooth transitions
    if (hasMultiple) {
      indices.add((currentIndex - 1 + total) % total)
      indices.add((currentIndex + 1) % total)
    }
    return indices
  }, [currentIndex, total, hasMultiple])

  // Listen to carousel changes
  useEffect(() => {
    if (!api) return

    const onSelect = () => {
      setCurrentIndex(api.selectedScrollSnap())
    }

    api.on('select', onSelect)
    return () => {
      api.off('select', onSelect)
    }
  }, [api])

  // Navigation handlers - stop all propagation to parent Link
  const stopEvent = useCallback((e: React.MouseEvent | React.PointerEvent) => {
    e.preventDefault()
    e.stopPropagation()
    e.nativeEvent.stopImmediatePropagation()
  }, [])

  const handlePrev = useCallback(
    (e: React.MouseEvent) => {
      stopEvent(e)
      api?.scrollPrev()
    },
    [api, stopEvent]
  )

  const handleNext = useCallback(
    (e: React.MouseEvent) => {
      stopEvent(e)
      api?.scrollNext()
    },
    [api, stopEvent]
  )

  // Dot click handler
  const handleDotClick = useCallback(
    (e: React.MouseEvent, index: number) => {
      e.preventDefault()
      e.stopPropagation()
      api?.scrollTo(index)
    },
    [api]
  )

  // Handle container click
  const handleClick = useCallback(
    (e: React.MouseEvent) => {
      // Don't trigger if clicking on navigation elements
      if ((e.target as HTMLElement).closest('[data-nav]')) {
        return
      }
      onClick?.()
    },
    [onClick]
  )

  // Empty state
  if (total === 0) {
    return (
      <div
        className={cn(containerClass, 'bg-muted flex items-center justify-center', className)}
        style={containerStyle}
      >
        <ImageOff className="w-8 h-8 text-muted-foreground/50" />
      </div>
    )
  }

  // Single image (or none) - no carousel needed
  if (!hasMultiple) {
    if (!firstImage) return null
    return (
      <div
        className={cn(containerClass, 'overflow-hidden group', className)}
        style={containerStyle}
        onClick={onClick}
      >
        <div className={cn(
          'w-full h-full transition-transform duration-500 ease-out',
          enableZoom && 'group-hover:scale-110'
        )}>
          <GalleryMedia
            media={firstImage}
            className="w-full h-full"
            priority
          />
        </div>
      </div>
    )
  }

  // Calculate visible dots
  const visibleDots = images.slice(0, maxDots).map((_, i) => i)
  const remainingCount = total > maxDots ? total - maxDots : 0

  // SSR fallback - render first image only to avoid hydration mismatch
  // The carousel requires DOM access and will cause issues during SSR
  if (!isMounted) {
    if (!firstImage) return null
    return (
      <div
        className={cn(containerClass, 'overflow-hidden', className)}
        style={containerStyle}
        onClick={onClick}
      >
        <GalleryMedia
          media={firstImage}
          className="w-full h-full"
          priority
        />
        {/* Show dots indicator placeholder for consistent layout */}
        {showDots && (
          <div
            className={cn(
              'absolute bottom-3 left-1/2 -translate-x-1/2 z-10',
              'flex items-center gap-1.5',
              'px-2 py-1 rounded-full',
              'bg-black/30 backdrop-blur-sm'
            )}
          >
            {visibleDots.map((index) => (
              <div
                key={index}
                className={cn(
                  'rounded-full',
                  index === 0
                    ? 'w-2 h-2 bg-white shadow-[0_0_4px_rgba(255,255,255,0.8)]'
                    : 'w-1.5 h-1.5 bg-white/50'
                )}
              />
            ))}
            {remainingCount > 0 && (
              <span className="text-white/80 text-[10px] font-medium ml-0.5">
                +{remainingCount}
              </span>
            )}
          </div>
        )}
        {/* Counter badge placeholder */}
        {showCounter && (
          <div className="absolute bottom-3 right-3 z-10 bg-black/50 backdrop-blur-sm text-white text-xs px-2 py-1 rounded-full font-medium">
            1 / {total}
          </div>
        )}
      </div>
    )
  }

  return (
    <div
      className={cn(containerClass, 'group/gallery', className)}
      style={containerStyle}
      onClick={handleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <Carousel
        key={carouselKey}
        setApi={setApi}
        opts={{
          loop: true,
        }}
        className="w-full h-full"
      >
        <CarouselContent className="-ml-0 h-full">
          {images.map((image, index) => {
            const shouldLoad = loadedIndices.has(index)
            const isActive = index === currentIndex

            return (
              <CarouselItem key={image.id} className="pl-0 h-full overflow-hidden">
                <div className={cn(
                  'w-full h-full transition-transform duration-500 ease-out',
                  enableZoom && isActive && isHovered && 'scale-110'
                )}>
                  {shouldLoad ? (
                    <GalleryMedia
                      media={image}
                      className="w-full h-full"
                      priority={index === 0}
                    />
                  ) : (
                    // Placeholder for unloaded images
                    <div className="w-full h-full bg-muted animate-pulse" />
                  )}
                </div>
              </CarouselItem>
            )
          })}
        </CarouselContent>
      </Carousel>

      {/* Navigation arrows - always visible but subtle, more prominent on hover */}
      {showArrows && (
        <>
          <button
            data-nav
            type="button"
            className={cn(
              'absolute left-2 top-1/2 -translate-y-1/2 z-10',
              'w-7 h-7 rounded-full',
              'bg-black/30 backdrop-blur-sm text-white/80',
              'flex items-center justify-center',
              'transition-all duration-200',
              // Always visible but subtle, more prominent on hover
              'opacity-60 group-hover/gallery:opacity-100',
              'hover:bg-black/60 hover:text-white hover:scale-110',
              'active:scale-95',
              'focus:outline-none focus:ring-2 focus:ring-white/50'
            )}
            onClick={handlePrev}
            onMouseDown={stopEvent}
            onPointerDown={stopEvent}
            aria-label="Previous image"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            data-nav
            type="button"
            className={cn(
              'absolute right-2 top-1/2 -translate-y-1/2 z-10',
              'w-7 h-7 rounded-full',
              'bg-black/30 backdrop-blur-sm text-white/80',
              'flex items-center justify-center',
              'transition-all duration-200',
              // Always visible but subtle, more prominent on hover
              'opacity-60 group-hover/gallery:opacity-100',
              'hover:bg-black/60 hover:text-white hover:scale-110',
              'active:scale-95',
              'focus:outline-none focus:ring-2 focus:ring-white/50'
            )}
            onClick={handleNext}
            onMouseDown={stopEvent}
            onPointerDown={stopEvent}
            aria-label="Next image"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </>
      )}

      {/* Dots indicator */}
      {showDots && (
        <div
          data-nav
          className={cn(
            'absolute bottom-3 left-1/2 -translate-x-1/2 z-10',
            'flex items-center gap-1.5',
            'px-2 py-1 rounded-full',
            'bg-black/30 backdrop-blur-sm'
          )}
          onClick={(e) => e.stopPropagation()}
        >
          {visibleDots.map((index) => (
            <button
              key={index}
              type="button"
              className={cn(
                'rounded-full transition-all duration-200',
                index === currentIndex
                  ? 'w-2 h-2 bg-white shadow-[0_0_4px_rgba(255,255,255,0.8)]'
                  : 'w-1.5 h-1.5 bg-white/50 hover:bg-white/80'
              )}
              onClick={(e) => handleDotClick(e, index)}
              aria-label={`Go to image ${index + 1}`}
            />
          ))}
          {remainingCount > 0 && (
            <span className="text-white/80 text-[10px] font-medium ml-0.5">
              +{remainingCount}
            </span>
          )}
        </div>
      )}

      {/* Counter badge */}
      {showCounter && (
        <div className="absolute bottom-3 right-3 z-10 bg-black/50 backdrop-blur-sm text-white text-xs px-2 py-1 rounded-full font-medium">
          {currentIndex + 1} / {total}
        </div>
      )}
    </div>
  )
})

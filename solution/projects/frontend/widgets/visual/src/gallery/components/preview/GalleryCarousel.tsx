'use client'

import * as React from 'react'
import { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { cn } from '@djangocfg/ui-core/lib'
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselPrevious,
  CarouselNext,
  type CarouselApi,
} from '@djangocfg/ui-core/components'
import { ZoomIn } from 'lucide-react'
import { GalleryMedia } from '../media'
import { GalleryThumbnails } from '../thumbnails'
import type { GalleryMediaItem } from '../../types'

export interface GalleryCarouselProps {
  images: GalleryMediaItem[]
  currentIndex: number
  total: number
  hasMultiple: boolean
  initialIndex?: number
  aspectRatio?: number
  showControls?: boolean
  showCounter?: boolean
  showThumbnails?: boolean
  enableLightbox?: boolean
  enableKeyboard?: boolean
  isLightboxOpen?: boolean
  onApiChange?: (api: CarouselApi | undefined) => void
  onIndexChange: (index: number) => void
  onLightboxOpen?: () => void
  onImageLoad?: () => void
  className?: string
}

/**
 * GalleryCarousel - Embla-based carousel for gallery images
 *
 * Features:
 * - Smooth slide transitions
 * - Touch/swipe support
 * - Keyboard navigation
 * - Mobile dots + desktop thumbnails
 */
export const GalleryCarousel = memo(function GalleryCarousel({
  images,
  currentIndex,
  total,
  hasMultiple,
  initialIndex = 0,
  aspectRatio = 16 / 9,
  showControls = true,
  showCounter = true,
  showThumbnails = true,
  enableLightbox = true,
  enableKeyboard = true,
  isLightboxOpen = false,
  onApiChange,
  onIndexChange,
  onLightboxOpen,
  onImageLoad,
  className,
}: GalleryCarouselProps) {
  const [api, setApi] = React.useState<CarouselApi>()
  // Track if component is mounted (client-side) to avoid hydration mismatches
  const [isMounted, setIsMounted] = useState(false)
  // Stable key for carousel reset on images change
  const carouselKey = images[0]?.id ?? 'empty'

  useEffect(() => {
    setIsMounted(true)
  }, [])

  // Notify parent when API is ready
  useEffect(() => {
    onApiChange?.(api)
  }, [api, onApiChange])

  // Mobile dots (max 5)
  const mobileDots = useMemo(() => {
    return images.slice(0, 5).map((_, index) => index)
  }, [images])

  const remainingCount = useMemo(() => {
    return images.length > 5 ? images.length - 5 : 0
  }, [images.length])

  // Sync carousel with external state
  useEffect(() => {
    if (!api) return
    api.scrollTo(currentIndex)
  }, [api, currentIndex])

  // Listen to carousel changes
  useEffect(() => {
    if (!api) return

    const onSelect = () => {
      const index = api.selectedScrollSnap()
      if (index !== currentIndex) {
        onIndexChange(index)
      }
    }

    api.on('select', onSelect)
    return () => {
      api.off('select', onSelect)
    }
  }, [api, currentIndex, onIndexChange])

  // Keyboard navigation
  useEffect(() => {
    if (!enableKeyboard || isLightboxOpen || !api) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft' && hasMultiple) {
        api.scrollPrev()
      } else if (e.key === 'ArrowRight' && hasMultiple) {
        api.scrollNext()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [enableKeyboard, isLightboxOpen, hasMultiple, api])

  // Dot click handler
  const handleDotClick = useCallback(
    (e: React.MouseEvent, index: number) => {
      e.stopPropagation()
      api?.scrollTo(index)
    },
    [api]
  )

  // Scroll to index
  const handleScrollTo = useCallback(
    (index: number) => {
      api?.scrollTo(index)
    },
    [api]
  )

  // Track pointer down position to distinguish click from drag
  const pointerStartRef = useRef<{ x: number; y: number; time: number } | null>(null)
  const CLICK_THRESHOLD = 10 // pixels
  const CLICK_TIME_THRESHOLD = 300 // ms

  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    pointerStartRef.current = { x: e.clientX, y: e.clientY, time: Date.now() }
  }, [])

  const handlePointerUp = useCallback((e: React.PointerEvent) => {
    if (!pointerStartRef.current || !enableLightbox || !onLightboxOpen) return

    const { x, y, time } = pointerStartRef.current
    const dx = Math.abs(e.clientX - x)
    const dy = Math.abs(e.clientY - y)
    const dt = Date.now() - time

    // Don't open lightbox when interacting with video controls
    const target = e.target as HTMLElement
    const isVideoInteraction =
      target.tagName === 'VIDEO' || target.closest('video, [data-nav]') !== null

    // Only trigger click if pointer didn't move much and was quick
    if (
      !isVideoInteraction &&
      dx < CLICK_THRESHOLD &&
      dy < CLICK_THRESHOLD &&
      dt < CLICK_TIME_THRESHOLD
    ) {
      onLightboxOpen()
    }

    pointerStartRef.current = null
  }, [enableLightbox, onLightboxOpen])

  // SSR fallback - render first image only to avoid hydration mismatch
  // The carousel requires DOM access and will cause issues during SSR
  if (!isMounted) {
    const firstImage = images[0]
    if (!firstImage) return null
    return (
      <div className={cn('space-y-3', className)}>
        <div className="relative rounded-xl overflow-hidden">
          <div
            className="relative bg-muted"
            style={{ aspectRatio }}
          >
            <GalleryMedia
              media={firstImage}
              className="w-full h-full"
              priority
            />
            {/* Dark overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-black/20 pointer-events-none" />
          </div>

          {/* Counter */}
          {showCounter && hasMultiple && (
            <div
              className={cn(
                'absolute bottom-3 right-3 z-10',
                'bg-black/60 backdrop-blur-sm text-white px-3 py-1.5 rounded-full',
                'text-sm font-medium'
              )}
            >
              1 / {total}
            </div>
          )}

          {/* Mobile dots */}
          {hasMultiple && (
            <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-2 md:hidden z-10">
              {mobileDots.map((index) => (
                <div
                  key={index}
                  className={cn(
                    'rounded-full',
                    index === 0
                      ? 'w-2.5 h-2.5 bg-white shadow-[0_0_4px_rgba(255,255,255,0.8)]'
                      : 'w-2 h-2 bg-white/40'
                  )}
                />
              ))}
              {remainingCount > 0 && (
                <span className="text-white/70 text-xs ml-1">+{remainingCount}</span>
              )}
            </div>
          )}
        </div>

        {/* Thumbnails placeholder */}
        {showThumbnails && hasMultiple && (
          <div className="hidden md:flex gap-2">
            {images.slice(0, 8).map((image, index) => (
              <div
                key={image.id}
                className={cn(
                  'w-16 h-16 rounded-lg overflow-hidden bg-muted flex-shrink-0',
                  index === 0 && 'ring-2 ring-primary'
                )}
              >
                <GalleryMedia
                  media={image}
                  className="w-full h-full"
                />
              </div>
            ))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className={cn('space-y-3', className)}>
      <Carousel
        key={carouselKey}
        setApi={setApi}
        opts={{
          loop: true,
          startIndex: initialIndex,
        }}
        className="relative rounded-xl overflow-hidden"
      >
        <CarouselContent className="-ml-0">
          {images.map((image, index) => (
            <CarouselItem key={image.id} className="pl-0">
              <div
                className={cn('relative bg-muted', enableLightbox && 'cursor-pointer')}
                style={{ aspectRatio }}
                onPointerDown={enableLightbox ? handlePointerDown : undefined}
                onPointerUp={enableLightbox ? handlePointerUp : undefined}
              >
                <GalleryMedia
                  media={image}
                  className="w-full h-full"
                  onLoad={index === currentIndex ? onImageLoad : undefined}
                  priority={index === 0}
                />

                {/* Dark overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-black/20 pointer-events-none" />

                {/* Lightbox indicator */}
                {enableLightbox && (
                  <div className="absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                    <div className="bg-black/60 backdrop-blur-sm rounded-full p-3 shadow-lg border border-white/20">
                      <ZoomIn className="w-6 h-6 text-white" />
                    </div>
                  </div>
                )}
              </div>
            </CarouselItem>
          ))}
        </CarouselContent>

        {/* Navigation Controls */}
        {showControls && hasMultiple && (
          <>
            <CarouselPrevious
              className={cn(
                'absolute left-3 top-1/2 -translate-y-1/2',
                'w-10 h-10 rounded-full',
                'bg-black/50 hover:bg-black/70 text-white backdrop-blur-sm border-white/20',
                'disabled:opacity-30'
              )}
            />
            <CarouselNext
              className={cn(
                'absolute right-3 top-1/2 -translate-y-1/2',
                'w-10 h-10 rounded-full',
                'bg-black/50 hover:bg-black/70 text-white backdrop-blur-sm border-white/20',
                'disabled:opacity-30'
              )}
            />
          </>
        )}

        {/* Counter */}
        {showCounter && hasMultiple && (
          <div
            className={cn(
              'absolute bottom-3 right-3 z-10',
              'bg-black/60 backdrop-blur-sm text-white px-3 py-1.5 rounded-full',
              'text-sm font-medium'
            )}
          >
            {currentIndex + 1} / {total}
          </div>
        )}

        {/* Mobile dots */}
        {hasMultiple && (
          <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-2 md:hidden z-10">
            {mobileDots.map((index) => (
              <button
                key={index}
                type="button"
                className={cn(
                  'rounded-full transition-all',
                  index === currentIndex
                    ? 'w-2.5 h-2.5 bg-white shadow-[0_0_4px_rgba(255,255,255,0.8)]'
                    : 'w-2 h-2 bg-white/40'
                )}
                onClick={(e) => handleDotClick(e, index)}
                aria-label={`Go to image ${index + 1}`}
              />
            ))}
            {remainingCount > 0 && (
              <span className="text-white/70 text-xs ml-1">+{remainingCount}</span>
            )}
          </div>
        )}
      </Carousel>

      {/* Thumbnails */}
      {showThumbnails && hasMultiple && (
        <GalleryThumbnails
          images={images}
          currentIndex={currentIndex}
          onSelect={handleScrollTo}
          size="md"
          className="hidden md:flex"
        />
      )}
    </div>
  )
})

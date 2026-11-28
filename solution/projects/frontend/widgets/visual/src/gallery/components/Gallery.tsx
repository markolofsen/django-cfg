'use client'

import { memo, useCallback, useMemo, Suspense, lazy } from 'react'
import { cn } from '@djangocfg/ui-core/lib'
import { useAppT } from '@djangocfg/i18n'
import { ImageOff } from 'lucide-react'
import { useGallery } from '../hooks/useGallery'
import { GalleryGrid } from './preview'
import { GalleryCarousel } from './preview'
import type { GalleryProps } from '../types'

// Lazy load lightbox - only loaded when user opens it
const GalleryLightbox = lazy(() =>
  import('./lightbox').then((mod) => ({ default: mod.GalleryLightbox }))
)

/**
 * Gallery - Complete image gallery with carousel/grid preview and lightbox
 *
 * Features:
 * - Two preview modes: carousel (default) or grid
 * - Smooth slide transitions (embla-carousel)
 * - Touch/swipe support
 * - Keyboard navigation
 * - Fullscreen lightbox
 * - Dark overlay for controls
 */
export const Gallery = memo(function Gallery({
  images,
  initialIndex = 0,
  previewMode = 'carousel',
  previewCount = 5,
  showThumbnails = true,
  showControls = true,
  showCounter = true,
  aspectRatio = 16 / 9,
  enableLightbox = true,
  enableKeyboard = true,
  onImageChange,
  onLightboxOpen,
  onLightboxClose,
  emptyState,
  className,
}: GalleryProps) {
  const t = useAppT()
  const noImagesText = useMemo(() => t('tools.gallery.noImages'), [t])

  const gallery = useGallery({
    images,
    initialIndex,
    loop: true,
    onImageChange,
  })

  const {
    currentIndex,
    total,
    hasMultiple,
    isLightboxOpen,
    goTo,
    openLightbox,
    closeLightbox,
    setLoading,
  } = gallery

  // Lightbox callbacks
  const handleLightboxOpen = useCallback(() => {
    openLightbox()
    onLightboxOpen?.()
  }, [openLightbox, onLightboxOpen])

  const handleLightboxClose = useCallback(() => {
    closeLightbox()
    onLightboxClose?.()
  }, [closeLightbox, onLightboxClose])

  // Open lightbox at specific index (for grid mode)
  const handleGridImageClick = useCallback(
    (index: number) => {
      goTo(index)
      openLightbox()
      onLightboxOpen?.()
    },
    [goTo, openLightbox, onLightboxOpen]
  )

  // Current image load handler
  const handleCurrentImageLoad = useCallback(() => {
    setLoading(false)
  }, [setLoading])

  // Empty state
  if (images.length === 0) {
    if (emptyState) {
      return <>{emptyState}</>
    }

    return (
      <div
        className={cn(
          'bg-muted rounded-xl flex items-center justify-center',
          className
        )}
        style={{ aspectRatio }}
      >
        <div className="text-center text-muted-foreground p-8">
          <ImageOff className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>{noImagesText}</p>
        </div>
      </div>
    )
  }

  // Grid mode
  if (previewMode === 'grid') {
    return (
      <div className={className}>
        <GalleryGrid
          images={images}
          maxVisible={previewCount}
          aspectRatio={aspectRatio}
          gap={2}
          rounded="xl"
          onImageClick={enableLightbox ? handleGridImageClick : undefined}
          showMoreBadge
        />

        {/* Lightbox - lazy loaded */}
        {enableLightbox && isLightboxOpen && (
          <Suspense fallback={null}>
            <GalleryLightbox
              open={isLightboxOpen}
              onClose={handleLightboxClose}
              images={images}
              currentIndex={currentIndex}
              onIndexChange={goTo}
              showThumbnails={showThumbnails}
            />
          </Suspense>
        )}
      </div>
    )
  }

  // Carousel mode (default)
  return (
    <>
      <GalleryCarousel
        images={images}
        currentIndex={currentIndex}
        total={total}
        hasMultiple={hasMultiple}
        initialIndex={initialIndex}
        aspectRatio={aspectRatio}
        showControls={showControls}
        showCounter={showCounter}
        showThumbnails={showThumbnails}
        enableLightbox={enableLightbox}
        enableKeyboard={enableKeyboard}
        isLightboxOpen={isLightboxOpen}
        onIndexChange={goTo}
        onLightboxOpen={handleLightboxOpen}
        onImageLoad={handleCurrentImageLoad}
        className={className}
      />

      {/* Lightbox - lazy loaded */}
      {enableLightbox && isLightboxOpen && (
        <Suspense fallback={null}>
          <GalleryLightbox
            open={isLightboxOpen}
            onClose={handleLightboxClose}
            images={images}
            currentIndex={currentIndex}
            onIndexChange={goTo}
            showThumbnails={showThumbnails}
          />
        </Suspense>
      )}
    </>
  )
})

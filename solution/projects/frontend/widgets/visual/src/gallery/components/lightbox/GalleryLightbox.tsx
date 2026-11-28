'use client'

import { memo, useEffect, useCallback, useState, useMemo, useRef } from 'react'
import { createPortal } from 'react-dom'
import { cn } from '@djangocfg/ui-core/lib'
import { useAppT } from '@djangocfg/i18n'
import { X, ChevronLeft, ChevronRight, Download, Share2, ZoomIn, ZoomOut } from 'lucide-react'
import { useSwipe } from '../../hooks/useSwipe'
import { usePreloadImages } from '../../hooks/usePreloadImages'
import { useZoom } from '../../hooks/useZoom'
import { GalleryMedia } from '../media'
import { GalleryThumbnails } from '../thumbnails'
import type { GalleryLightboxProps } from '../../types'

// Liquid-glass control — token-driven (--card / --foreground), so it stays
// legible on BOTH the light scrim and the dark vibrancy backdrop. Foreground
// icon color flips with the theme; hover wash adapts via the foreground token.
const GLASS_BTN =
  'glass-liquid text-foreground/80 transition-colors ' +
  'hover:text-foreground hover:bg-[color-mix(in_oklab,var(--foreground)_12%,transparent)] ' +
  'focus:outline-none focus-visible:ring-2 focus-visible:ring-ring'

/**
 * GalleryLightbox - Fullscreen image viewer with zoom and navigation
 *
 * Features:
 * - Preloads adjacent images for smooth navigation
 * - Loading skeleton while image loads
 * - Zoom with pan/drag support
 * - Keyboard navigation (arrows, Home/End, Esc), focus trap, backdrop click
 * - Swipe navigation
 */
export const GalleryLightbox = memo(function GalleryLightbox({
  open,
  onClose,
  images,
  currentIndex,
  onIndexChange,
  showThumbnails = true,
  enableZoom = true,
  enableDownload = true,
  enableShare = true,
  title,
}: GalleryLightboxProps) {
  const t = useAppT()
  const [mounted, setMounted] = useState(false)
  const dialogRef = useRef<HTMLDivElement>(null)
  // Element focused before the lightbox opened, restored on close
  const previousFocusRef = useRef<HTMLElement | null>(null)

  // Translations
  const labels = useMemo(() => ({
    lightbox: t('tools.gallery.lightbox'),
    previous: t('tools.gallery.previous'),
    next: t('tools.gallery.next'),
    close: t('tools.gallery.close'),
    download: t('tools.gallery.download'),
    share: t('tools.gallery.share'),
    zoomIn: t('tools.image.zoomIn'),
    zoomOut: t('tools.image.zoomOut'),
  }), [t])

  // Unified zoom (handles both desktop click/drag and mobile pinch/tap)
  const zoom = useZoom({
    minScale: 1,
    maxScale: 3,
    desktopScale: 2,
  })

  // Prepare data
  const currentImage = useMemo(() => images[currentIndex], [images, currentIndex])
  const hasMultiple = useMemo(() => images.length > 1, [images.length])
  const isVideo = currentImage?.type === 'video' && Boolean(currentImage.videoSrc)
  const { isZoomed, isDragging } = zoom
  const resetZoom = zoom.reset

  // Preload adjacent images when lightbox is open
  usePreloadImages(open ? images : [], currentIndex, 2)

  // Handle client-side mounting for portal
  useEffect(() => {
    setMounted(true)
  }, [])

  // Reset zoom when image changes
  useEffect(() => {
    resetZoom()
  }, [currentIndex, resetZoom])

  // Prevent body scroll when open
  useEffect(() => {
    if (!open) return
    const originalStyle = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = originalStyle
    }
  }, [open])

  // Focus management: move focus into the dialog on open, restore on close
  useEffect(() => {
    if (!open || !mounted) return
    previousFocusRef.current = document.activeElement as HTMLElement | null
    // Defer to allow the portal content to mount
    const id = window.requestAnimationFrame(() => {
      dialogRef.current?.focus()
    })
    return () => {
      window.cancelAnimationFrame(id)
      previousFocusRef.current?.focus?.()
    }
  }, [open, mounted])

  // Navigation handlers
  const goToPrev = useCallback(() => {
    if (hasMultiple) {
      onIndexChange((currentIndex - 1 + images.length) % images.length)
    }
  }, [hasMultiple, currentIndex, images.length, onIndexChange])

  const goToNext = useCallback(() => {
    if (hasMultiple) {
      onIndexChange((currentIndex + 1) % images.length)
    }
  }, [hasMultiple, currentIndex, images.length, onIndexChange])

  // Keyboard navigation + focus trap
  useEffect(() => {
    if (!open) return

    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'Escape':
          e.preventDefault()
          if (isZoomed) {
            resetZoom()
          } else {
            onClose()
          }
          break
        case 'ArrowLeft':
          if (!isZoomed) goToPrev()
          break
        case 'ArrowRight':
          if (!isZoomed) goToNext()
          break
        case 'Home':
          if (!isZoomed && hasMultiple) {
            e.preventDefault()
            onIndexChange(0)
          }
          break
        case 'End':
          if (!isZoomed && hasMultiple) {
            e.preventDefault()
            onIndexChange(images.length - 1)
          }
          break
        case 'Tab': {
          // Trap focus within the dialog
          const dialog = dialogRef.current
          if (!dialog) break
          const focusable = dialog.querySelectorAll<HTMLElement>(
            'button:not([disabled]), [href], [tabindex]:not([tabindex="-1"])'
          )
          const first = focusable[0]
          const last = focusable[focusable.length - 1]
          if (!first || !last) {
            e.preventDefault()
            break
          }
          const active = document.activeElement
          if (e.shiftKey && (active === first || active === dialog)) {
            e.preventDefault()
            last.focus()
          } else if (!e.shiftKey && active === last) {
            e.preventDefault()
            first.focus()
          }
          break
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [open, isZoomed, goToPrev, goToNext, onClose, resetZoom, hasMultiple, images.length, onIndexChange])

  // Swipe handlers (disabled when zoomed)
  const swipeHandlers = useSwipe({
    onSwipeLeft: isZoomed ? undefined : goToNext,
    onSwipeRight: isZoomed ? undefined : goToPrev,
  })

  // Action handlers
  const handleDownload = useCallback(() => {
    if (!currentImage) return
    // For videos download the video file, otherwise the image
    const downloadUrl = isVideo ? currentImage.videoSrc! : currentImage.src
    // Derive a filename from the URL path, fall back to a numbered name
    let filename = isVideo ? `video-${currentIndex + 1}.mp4` : `image-${currentIndex + 1}.jpg`
    try {
      const path = new URL(downloadUrl, window.location.href).pathname
      const last = path.split('/').pop()
      if (last && /\.[a-z0-9]+$/i.test(last)) {
        filename = decodeURIComponent(last)
      }
    } catch {
      // Keep fallback filename
    }
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename
    link.rel = 'noopener'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }, [currentImage, currentIndex, isVideo])

  const handleShare = useCallback(async () => {
    if (!currentImage) return
    if (navigator.share) {
      try {
        await navigator.share({
          title: title || 'Image',
          url: currentImage.src,
        })
      } catch {
        // User cancelled or error
      }
    } else {
      await navigator.clipboard.writeText(currentImage.src)
    }
  }, [currentImage, title])

  const handleToggleZoom = useCallback(() => {
    zoom.toggleZoom()
  }, [zoom])

  // Close only when the backdrop itself (not a child) is clicked
  const handleBackdropClick = useCallback((e: React.MouseEvent) => {
    if (e.target === e.currentTarget) onClose()
  }, [onClose])

  if (!open || !mounted) return null

  const lightbox = (
    <div
      ref={dialogRef}
      className={cn(
        'fixed inset-0 z-50',
        // Theme-aware Quick-Look scrim: a LIGHT neutral wash in light mode so
        // the lightbox feels native (Quick Look matches system appearance),
        // a deep vibrancy floor in dark mode. blur+saturate in both so the
        // page behind bleeds through softly and the image floats.
        'backdrop-blur-2xl backdrop-saturate-150',
        '[background-color:color-mix(in_oklab,var(--background)_72%,transparent)]',
        'dark:[background-color:color-mix(in_oklab,#000_82%,transparent)]',
        'animate-in fade-in-0 duration-200',
        'focus:outline-none'
      )}
      role="dialog"
      aria-modal="true"
      aria-label={title || labels.lightbox}
      tabIndex={-1}
    >
      {/* Content */}
      <div
        className="relative w-full h-full flex flex-col"
        {...swipeHandlers}
      >
        {/* Header */}
        <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between p-4">
          {/* Title & Counter — liquid-glass pill so it reads on both the light
              and dark scrim (glass-liquid is token-driven, foreground text
              flips with the theme). */}
          {(title || hasMultiple) ? (
            <div className="glass-liquid rounded-2xl px-3 py-1.5 text-foreground">
              {title && <div className="font-medium">{title}</div>}
              {hasMultiple && (
                <div className="text-sm text-foreground/70" aria-live="polite">
                  {currentIndex + 1} / {images.length}
                </div>
              )}
            </div>
          ) : (
            <span aria-hidden />
          )}

          {/* Actions */}
          <div className="flex items-center gap-2">
            {enableZoom && !isVideo && (
              <button
                type="button"
                className={cn(GLASS_BTN, 'p-2 rounded-full')}
                onClick={handleToggleZoom}
                aria-label={isZoomed ? labels.zoomOut : labels.zoomIn}
              >
                {isZoomed ? (
                  <ZoomOut className="w-5 h-5" />
                ) : (
                  <ZoomIn className="w-5 h-5" />
                )}
              </button>
            )}

            {enableDownload && (
              <button
                type="button"
                className={cn(GLASS_BTN, 'p-2 rounded-full')}
                onClick={handleDownload}
                aria-label={labels.download}
              >
                <Download className="w-5 h-5" />
              </button>
            )}

            {enableShare && (
              <button
                type="button"
                className={cn(GLASS_BTN, 'p-2 rounded-full')}
                onClick={handleShare}
                aria-label={labels.share}
              >
                <Share2 className="w-5 h-5" />
              </button>
            )}

            <button
              type="button"
              className={cn(GLASS_BTN, 'p-2 rounded-full')}
              onClick={onClose}
              aria-label={labels.close}
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Main Image */}
        <div
          className="flex-1 flex items-center justify-center p-4 pt-16 pb-24 overflow-hidden"
          onClick={handleBackdropClick}
        >
          {currentImage && (
            <div
              className={cn(
                'relative w-full h-full select-none',
                // Zoom cursors only apply to images, not video (needs native controls)
                !isVideo && (isZoomed ? 'cursor-grab' : enableZoom ? 'cursor-zoom-in' : 'cursor-default'),
                !isVideo && isDragging && 'cursor-grabbing'
              )}
              {...(enableZoom && !isVideo ? zoom.handlers : {})}
              style={{
                transform: isZoomed && !isVideo
                  ? `scale(${zoom.state.scale}) translate(${zoom.state.x}px, ${zoom.state.y}px)`
                  : 'scale(1)',
                transition: isDragging ? 'none' : 'transform 0.3s ease-out',
                touchAction: 'none',
              }}
            >
              <GalleryMedia
                media={currentImage}
                // pointer-events disabled for images so the zoom wrapper gets clicks;
                // video needs pointer events for its native/overlay controls
                className={cn('w-full h-full', !isVideo && 'pointer-events-none')}
                objectFit="contain"
                showLoading
                priority
                autoPlay
              />
            </div>
          )}
        </div>

        {/* Navigation Arrows */}
        {hasMultiple && !isZoomed && (
          <>
            <button
              type="button"
              className={cn(
                GLASS_BTN,
                'absolute left-4 top-1/2 -translate-y-1/2 z-10',
                'w-12 h-12 rounded-full',
                'flex items-center justify-center'
              )}
              onClick={goToPrev}
              aria-label={labels.previous}
            >
              <ChevronLeft className="w-6 h-6" />
            </button>

            <button
              type="button"
              className={cn(
                GLASS_BTN,
                'absolute right-4 top-1/2 -translate-y-1/2 z-10',
                'w-12 h-12 rounded-full',
                'flex items-center justify-center'
              )}
              onClick={goToNext}
              aria-label={labels.next}
            >
              <ChevronRight className="w-6 h-6" />
            </button>
          </>
        )}

        {/* Thumbnails */}
        {showThumbnails && hasMultiple && !isZoomed && (
          <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-white/40 dark:from-black/50 to-transparent">
            <GalleryThumbnails
              images={images}
              currentIndex={currentIndex}
              onSelect={onIndexChange}
              size="sm"
              className="justify-center"
            />
          </div>
        )}
      </div>
    </div>
  )

  return createPortal(lightbox, document.body)
})

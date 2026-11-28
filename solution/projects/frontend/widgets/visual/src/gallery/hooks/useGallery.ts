'use client'

import { useCallback, useEffect, useMemo, useState } from 'react';

import type { GalleryMediaItem, GalleryContextValue } from '../types'

export interface UseGalleryOptions {
  /** Array of images */
  images: GalleryMediaItem[]
  /** Initial selected index */
  initialIndex?: number
  /** Loop navigation */
  loop?: boolean
  /** Callback when image changes */
  onImageChange?: (index: number, image: GalleryMediaItem) => void
}

/**
 * Hook for managing gallery state
 */
export function useGallery({
  images,
  initialIndex = 0,
  loop = true,
  onImageChange,
}: UseGalleryOptions): GalleryContextValue {
  const [currentIndex, setCurrentIndex] = useState(initialIndex)
  const [isLightboxOpen, setIsLightboxOpen] = useState(false)
  const [isZoomed, setIsZoomed] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const total = images.length
  const hasMultiple = total > 1
  const currentImage = images[currentIndex] ?? null

  // Reset state when images change
  useEffect(() => {
    if (currentIndex >= total) {
      setCurrentIndex(Math.max(0, total - 1))
    }
  }, [total, currentIndex])

  // Reset zoom when image changes
  useEffect(() => {
    setIsZoomed(false)
    setIsLoading(true)
  }, [currentIndex])

  const goTo = useCallback(
    (index: number) => {
      if (index < 0 || index >= total) return
      setCurrentIndex(index)
      onImageChange?.(index, images[index]!)
    },
    [total, images, onImageChange]
  )

  const next = useCallback(() => {
    if (!hasMultiple) return
    const nextIndex = loop
      ? (currentIndex + 1) % total
      : Math.min(currentIndex + 1, total - 1)
    if (nextIndex !== currentIndex) {
      goTo(nextIndex)
    }
  }, [currentIndex, total, hasMultiple, loop, goTo])

  const prev = useCallback(() => {
    if (!hasMultiple) return
    const prevIndex = loop
      ? (currentIndex - 1 + total) % total
      : Math.max(currentIndex - 1, 0)
    if (prevIndex !== currentIndex) {
      goTo(prevIndex)
    }
  }, [currentIndex, total, hasMultiple, loop, goTo])

  const openLightbox = useCallback((index?: number) => {
    if (index !== undefined) {
      setCurrentIndex(index)
    }
    setIsLightboxOpen(true)
    setIsZoomed(false)
  }, [])

  const closeLightbox = useCallback(() => {
    setIsLightboxOpen(false)
    setIsZoomed(false)
  }, [])

  const toggleZoom = useCallback(() => {
    setIsZoomed((prev) => !prev)
  }, [])

  const setLoadingState = useCallback((loading: boolean) => {
    setIsLoading(loading)
  }, [])

  return useMemo(
    () => ({
      // State
      currentIndex,
      isLightboxOpen,
      isZoomed,
      isLoading,
      // Computed
      images,
      currentImage,
      total,
      hasMultiple,
      // Actions
      goTo,
      next,
      prev,
      openLightbox,
      closeLightbox,
      toggleZoom,
      setLoading: setLoadingState,
    }),
    [
      currentIndex,
      isLightboxOpen,
      isZoomed,
      isLoading,
      images,
      currentImage,
      total,
      hasMultiple,
      goTo,
      next,
      prev,
      openLightbox,
      closeLightbox,
      toggleZoom,
      setLoadingState,
    ]
  )
}

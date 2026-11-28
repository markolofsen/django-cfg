'use client'

import { useEffect, useMemo, useRef, useState } from 'react';

import type { GalleryMediaItem } from '../types'

/**
 * Image with loaded dimensions
 */
export interface ImageWithDimensions extends GalleryMediaItem {
  width: number
  height: number
  loaded: boolean
}

/**
 * Result of useImageDimensions hook
 */
export interface UseImageDimensionsResult {
  /** Images with dimensions (loaded or from props) */
  images: ImageWithDimensions[]
  /** Whether all images have dimensions */
  isReady: boolean
  /** Whether currently loading */
  isLoading: boolean
  /** Number of images loaded */
  loadedCount: number
}

/**
 * Options for useImageDimensions
 */
export interface UseImageDimensionsOptions {
  /** Only load dimensions for first N images */
  maxToLoad?: number
  /** Skip loading if dimensions already present */
  skipIfPresent?: boolean
  /** Timeout per image in ms */
  timeout?: number
}

// Cache for loaded dimensions
const dimensionsCache = new Map<string, { width: number; height: number }>()

/**
 * Load image dimensions
 */
function loadImageDimensions(
  src: string,
  timeout: number = 5000
): Promise<{ width: number; height: number }> {
  // Check cache
  const cached = dimensionsCache.get(src)
  if (cached) return Promise.resolve(cached)

  return new Promise((resolve, reject) => {
    const img = new Image()
    const timeoutId = setTimeout(() => {
      reject(new Error('Timeout loading image'))
    }, timeout)

    img.onload = () => {
      clearTimeout(timeoutId)
      const dims = { width: img.naturalWidth, height: img.naturalHeight }
      dimensionsCache.set(src, dims)
      resolve(dims)
    }

    img.onerror = () => {
      clearTimeout(timeoutId)
      reject(new Error('Failed to load image'))
    }

    img.src = src
  })
}

/**
 * Hook to load image dimensions for gallery images
 *
 * Uses thumbnail URL when available (faster to load)
 * Caches results to avoid reloading
 */
export function useImageDimensions(
  images: GalleryMediaItem[],
  options: UseImageDimensionsOptions = {}
): UseImageDimensionsResult {
  const {
    maxToLoad = 5,
    skipIfPresent = true,
    timeout = 5000,
  } = options

  // Create stable key from image IDs
  const imageIds = useMemo(() => {
    return images.slice(0, maxToLoad).map(img => img.id).join(',')
  }, [images, maxToLoad])

  // Track dimensions in a map by ID (stable across re-renders)
  const dimensionsRef = useRef(new Map<string, { width: number; height: number; loaded: boolean }>())
  const [version, setVersion] = useState(0) // Force re-render when dimensions load
  const [isLoading, setIsLoading] = useState(true)
  const loadingRef = useRef(false)
  const prevImageIdsRef = useRef('')

  // Initialize dimensions from props or cache
  useEffect(() => {
    const targetImages = images.slice(0, maxToLoad)
    const idsChanged = prevImageIdsRef.current !== imageIds
    prevImageIdsRef.current = imageIds

    // Update dimensions map with any new images
    for (const img of targetImages) {
      if (!dimensionsRef.current.has(img.id)) {
        // Check cache first
        const src = img.thumbnail || img.src
        const cached = dimensionsCache.get(src)

        if (cached) {
          dimensionsRef.current.set(img.id, { ...cached, loaded: true })
        } else if (img.width && img.height && skipIfPresent) {
          dimensionsRef.current.set(img.id, { width: img.width, height: img.height, loaded: true })
        } else {
          dimensionsRef.current.set(img.id, { width: 0, height: 0, loaded: false })
        }
      }
    }

    // Find images that need loading
    const toLoad = targetImages.filter(img => {
      const dims = dimensionsRef.current.get(img.id)
      return !dims?.loaded
    })

    // Nothing to load
    if (toLoad.length === 0) {
      setIsLoading(false)
      if (idsChanged) setVersion(v => v + 1)
      return
    }

    // Already loading
    if (loadingRef.current) return

    loadingRef.current = true
    setIsLoading(true)

    // Load dimensions
    Promise.all(
      toLoad.map(async (img) => {
        try {
          const src = img.thumbnail || img.src
          const dims = await loadImageDimensions(src, timeout)
          dimensionsRef.current.set(img.id, { ...dims, loaded: true })
          return { id: img.id, success: true }
        } catch {
          // Use default dimensions on error
          dimensionsRef.current.set(img.id, { width: 1600, height: 900, loaded: true })
          return { id: img.id, success: false }
        }
      })
    ).then(() => {
      loadingRef.current = false
      setIsLoading(false)
      setVersion(v => v + 1)
    })
  }, [imageIds, images, maxToLoad, skipIfPresent, timeout])

  // Build result array
  const result = useMemo((): ImageWithDimensions[] => {
    return images.slice(0, maxToLoad).map(img => {
      const dims = dimensionsRef.current.get(img.id)
      return {
        ...img,
        width: dims?.width || img.width || 0,
        height: dims?.height || img.height || 0,
        loaded: dims?.loaded || false,
      }
    })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [imageIds, version])

  // Also return all images (not just maxToLoad) with available dimensions
  const allImages = useMemo((): ImageWithDimensions[] => {
    return images.map(img => {
      const dims = dimensionsRef.current.get(img.id)
      return {
        ...img,
        width: dims?.width || img.width || 0,
        height: dims?.height || img.height || 0,
        loaded: dims?.loaded || Boolean(img.width && img.height),
      }
    })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [images, version])

  const loadedCount = result.filter(img => img.loaded).length
  const targetCount = Math.min(images.length, maxToLoad)

  const isReady = !isLoading && loadedCount >= targetCount

  return {
    images: allImages,
    isReady,
    isLoading,
    loadedCount,
  }
}

/**
 * Clear dimensions cache
 */
export function clearDimensionsCache(): void {
  dimensionsCache.clear()
}

/**
 * Get cached dimensions for an image
 */
export function getCachedDimensions(
  src: string
): { width: number; height: number } | null {
  return dimensionsCache.get(src) || null
}

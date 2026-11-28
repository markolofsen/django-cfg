'use client'

import { useEffect, useRef } from 'react';

import type { GalleryMediaItem } from '../types'
import { normalizeImageUrl } from '../utils'

/** Max number of URLs to remember as "already preloaded" before evicting oldest */
const MAX_PRELOAD_MEMORY = 200

/**
 * Preload adjacent images for smoother navigation
 * Preloads prev and next images when current index changes
 */
export function usePreloadImages(
  images: GalleryMediaItem[],
  currentIndex: number,
  preloadCount: number = 1
): void {
  // Insertion-ordered Set, used as a bounded LRU to avoid unbounded growth
  const preloadedRef = useRef<Set<string>>(new Set())

  useEffect(() => {
    if (images.length === 0) return

    const toPreload: string[] = []

    // Collect indices to preload (current + adjacent)
    for (let offset = -preloadCount; offset <= preloadCount; offset++) {
      if (offset === 0) continue // Skip current, it's already loading

      const index = (currentIndex + offset + images.length) % images.length
      const image = images[index]
      if (!image) continue

      // Videos are not preloadable via Image(); skip them
      if (image.type === 'video') continue

      const src = normalizeImageUrl(image.src)
      if (src && !preloadedRef.current.has(src)) {
        toPreload.push(src)
      }
    }

    if (toPreload.length === 0) return

    const memory = preloadedRef.current
    const loaders: HTMLImageElement[] = []

    toPreload.forEach((src) => {
      const img = new Image()
      // Release the loader once finished so it can be GC'd
      const cleanup = () => {
        img.onload = null
        img.onerror = null
      }
      img.onload = cleanup
      img.onerror = cleanup
      img.src = src
      loaders.push(img)

      memory.add(src)
      // Evict oldest entries to keep the Set bounded
      if (memory.size > MAX_PRELOAD_MEMORY) {
        const oldest = memory.values().next().value
        if (oldest !== undefined) memory.delete(oldest)
      }
    })

    // Cancel in-flight loaders if the effect re-runs before they settle
    return () => {
      loaders.forEach((img) => {
        img.onload = null
        img.onerror = null
        img.src = ''
      })
    }
  }, [images, currentIndex, preloadCount])
}

/**
 * Preload specific image URLs
 */
export function preloadImage(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    const cleanup = () => {
      img.onload = null
      img.onerror = null
    }
    img.onload = () => {
      cleanup()
      resolve()
    }
    img.onerror = () => {
      cleanup()
      reject(new Error(`Failed to preload image: ${src}`))
    }
    img.src = normalizeImageUrl(src)
  })
}

/**
 * Preload multiple images with optional concurrency limit
 */
export async function preloadImages(
  urls: string[],
  concurrency: number = 3
): Promise<void> {
  const chunks: string[][] = []

  for (let i = 0; i < urls.length; i += concurrency) {
    chunks.push(urls.slice(i, i + concurrency))
  }

  for (const chunk of chunks) {
    await Promise.allSettled(chunk.map(preloadImage))
  }
}

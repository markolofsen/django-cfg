import type { GalleryMediaItem } from '../types'

/**
 * Image orientation types
 */
export type ImageOrientation = 'landscape' | 'portrait' | 'square'

/**
 * Analyzed image with orientation info
 */
export interface AnalyzedImage extends GalleryMediaItem {
  orientation: ImageOrientation
  aspectRatio: number
}

/**
 * Get orientation from width/height
 */
export function getOrientation(width?: number, height?: number): ImageOrientation {
  if (!width || !height) return 'landscape' // default assumption

  const ratio = width / height
  if (ratio > 1.2) return 'landscape'
  if (ratio < 0.8) return 'portrait'
  return 'square'
}

/**
 * Calculate aspect ratio from width/height
 */
export function getAspectRatio(width?: number, height?: number): number {
  if (!width || !height) return 16 / 9 // default
  return width / height
}

/**
 * Analyze single image
 */
export function analyzeImage(image: GalleryMediaItem): AnalyzedImage {
  return {
    ...image,
    orientation: getOrientation(image.width, image.height),
    aspectRatio: getAspectRatio(image.width, image.height),
  }
}

/**
 * Analyze array of images
 */
export function analyzeImages(images: GalleryMediaItem[]): AnalyzedImage[] {
  return images.map(analyzeImage)
}

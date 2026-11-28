'use client'

import { memo } from 'react'
import { GalleryImage as GalleryImageComponent } from './GalleryImage'
import { GalleryVideo } from './GalleryVideo'
import type { GalleryMediaItem } from '../../types'

export interface GalleryMediaProps {
  /** Media data */
  media: GalleryMediaItem
  /** Whether to show loading skeleton */
  showLoading?: boolean
  /** On load callback */
  onLoad?: () => void
  /** On error callback */
  onError?: () => void
  /** On click callback */
  onClick?: () => void
  /** Priority loading (images only) */
  priority?: boolean
  /** Autoplay video */
  autoPlay?: boolean
  /** Object fit mode: cover for thumbnails/grid, contain for lightbox */
  objectFit?: 'cover' | 'contain'
  /** Additional CSS class */
  className?: string
}

/**
 * GalleryMedia - Renders image or video based on media type
 */
export const GalleryMedia = memo(function GalleryMedia({
  media,
  showLoading = true,
  onLoad,
  onError,
  onClick,
  priority = false,
  autoPlay = false,
  objectFit = 'cover',
  className,
}: GalleryMediaProps) {
  const isVideo = media.type === 'video' && media.videoSrc

  if (isVideo) {
    return (
      <GalleryVideo
        media={media}
        autoPlay={autoPlay}
        muted
        loop
        showControls
        className={className}
      />
    )
  }

  return (
    <GalleryImageComponent
      image={media}
      showLoading={showLoading}
      onLoad={onLoad}
      onError={onError}
      onClick={onClick}
      priority={priority}
      objectFit={objectFit}
      className={className}
    />
  )
})

'use client'

import { memo, useMemo } from 'react'
import { cn } from '@djangocfg/ui-core/lib'
import { useAppT } from '@djangocfg/i18n'
import { useImageLoader } from '@djangocfg/ui-core/hooks'
import { ImageOff } from 'lucide-react'
import type { GalleryImageProps } from '../../types'
import { normalizeImageUrl } from '../../utils'
import { ImageSpinner } from '../shared'

/**
 * GalleryImage - Single image with loading state and error handling
 * Uses CSS background-image for cover mode, <img> for contain mode
 */
export const GalleryImage = memo(function GalleryImage({
  image,
  showLoading = true,
  onLoad,
  onError,
  onClick,
  // Accepted but not yet honoured: the fetch is driven by `useImageLoader`'s
  // `Image()`, which has no priority hint to forward. Threading one through is
  // a change to that hook, not to this component.
  priority: _priority = false,
  objectFit = 'cover',
  className,
}: GalleryImageProps) {
  const t = useAppT()
  const failedToLoadText = useMemo(() => t('tools.image.failedToLoad'), [t])
  const normalizedSrc = useMemo(() => normalizeImageUrl(image.src), [image.src])
  const callbacks = useMemo(() => ({ onLoad, onError }), [onLoad, onError])
  const { isLoading, isLoaded, hasError } = useImageLoader(normalizedSrc, callbacks)

  const backgroundStyle = useMemo(() =>
    isLoaded && objectFit === 'cover' ? {
      backgroundImage: `url(${normalizedSrc})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat',
    } : undefined
  , [isLoaded, normalizedSrc, objectFit])

  if (hasError) {
    return (
      <div
        className={cn(
          'flex items-center justify-center bg-muted',
          className
        )}
      >
        <div className="text-center text-muted-foreground">
          <ImageOff className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p className="text-sm">{failedToLoadText}</p>
        </div>
      </div>
    )
  }

  // Use <img> tag for contain mode (lightbox)
  if (objectFit === 'contain') {
    return (
      <div
        className={cn(
          'relative w-full h-full flex items-center justify-center bg-muted',
          className
        )}
        onClick={onClick}
      >
        {/* Loading spinner */}
        {isLoading && showLoading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <ImageSpinner size="lg" />
          </div>
        )}
        {isLoaded && (
          <img
            src={normalizedSrc}
            alt={image.alt || 'Gallery image'}
            className="max-w-full max-h-full object-contain animate-in fade-in-0 duration-300"
          />
        )}
      </div>
    )
  }

  // Use background-image for cover mode (thumbnails, grid)
  return (
    <div
      className={cn(
        'relative w-full h-full bg-muted',
        isLoaded && 'animate-in fade-in-0 duration-300',
        className
      )}
      style={backgroundStyle}
      onClick={onClick}
      role="img"
      aria-label={image.alt || 'Gallery image'}
    >
      {/* Loading spinner */}
      {isLoading && showLoading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <ImageSpinner size="md" />
        </div>
      )}
    </div>
  )
})

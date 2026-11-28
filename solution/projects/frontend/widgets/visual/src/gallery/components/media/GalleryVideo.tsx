'use client'

import { memo, useCallback, useMemo, useRef, useState } from 'react'
import { cn } from '@djangocfg/ui-core/lib'
import { useAppT } from '@djangocfg/i18n'
import { Play, Pause, Volume2, VolumeX, Maximize, AlertCircle } from 'lucide-react'
import type { GalleryMediaItem } from '../../types'

export interface GalleryVideoProps {
  /** Video data */
  media: GalleryMediaItem
  /** Whether video should autoplay */
  autoPlay?: boolean
  /** Whether video should be muted by default */
  muted?: boolean
  /** Whether video should loop */
  loop?: boolean
  /** Show controls overlay */
  showControls?: boolean
  /** Additional CSS class */
  className?: string
}

/**
 * GalleryVideo - Video player for gallery items
 */
export const GalleryVideo = memo(function GalleryVideo({
  media,
  autoPlay = false,
  muted = true,
  loop = true,
  showControls = true,
  className,
}: GalleryVideoProps) {
  const t = useAppT()
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isPlaying, setIsPlaying] = useState(autoPlay)
  const [isMuted, setIsMuted] = useState(muted)
  const [showOverlay, setShowOverlay] = useState(true)
  const [hasError, setHasError] = useState(false)

  const labels = useMemo(() => ({
    play: t('tools.video.play'),
    fullscreen: t('tools.video.fullscreen'),
    unavailable: t('tools.video.unavailable'),
  }), [t])

  const handlePlayPause = useCallback((e?: React.MouseEvent) => {
    e?.stopPropagation()
    const video = videoRef.current
    if (!video) return

    if (video.paused) {
      // play() returns a promise that can reject (autoplay policy / no source)
      const playPromise = video.play()
      if (playPromise && typeof playPromise.then === 'function') {
        playPromise.then(() => setIsPlaying(true)).catch(() => setIsPlaying(false))
      } else {
        setIsPlaying(true)
      }
    } else {
      video.pause()
      setIsPlaying(false)
    }
  }, [])

  const handleMuteToggle = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    const video = videoRef.current
    if (!video) return

    video.muted = !video.muted
    setIsMuted(video.muted)
  }, [])

  const handleFullscreen = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    const video = videoRef.current
    if (!video) return

    if (video.requestFullscreen) {
      video.requestFullscreen()
    }
  }, [])

  const handleVideoClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    handlePlayPause()
  }, [handlePlayPause])

  const handleMouseEnter = useCallback(() => {
    setShowOverlay(true)
  }, [])

  const handleMouseLeave = useCallback(() => {
    if (isPlaying) {
      setShowOverlay(false)
    }
  }, [isPlaying])

  const handleError = useCallback(() => {
    setHasError(true)
    setIsPlaying(false)
  }, [])

  // Keep local state in sync with native video events (native controls, end of playback)
  const handlePlay = useCallback(() => setIsPlaying(true), [])
  const handlePause = useCallback(() => setIsPlaying(false), [])
  const handleEnded = useCallback(() => {
    setIsPlaying(false)
    setShowOverlay(true)
  }, [])

  const handleContainerClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
  }, [])

  if (!media.videoSrc) {
    return null
  }

  // Error state - show poster with error overlay
  if (hasError) {
    return (
      <div
        data-nav
        className={cn('relative w-full h-full bg-black', className)}
        onClick={handleContainerClick}
      >
        {media.src && (
          <img
            src={media.src}
            alt={media.alt || 'Video thumbnail'}
            className="w-full h-full object-contain opacity-50"
          />
        )}
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/50">
          <AlertCircle className="w-12 h-12 text-white/70 mb-2" />
          <span className="text-white/70 text-sm">{labels.unavailable}</span>
        </div>
        <div className="absolute top-3 left-3 px-2 py-1 bg-black/60 rounded text-white text-xs font-medium">
          Video
        </div>
      </div>
    )
  }

  return (
    <div
      data-nav
      className={cn('relative w-full h-full bg-black', className)}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={handleContainerClick}
    >
      <video
        ref={videoRef}
        className="w-full h-full object-contain"
        src={media.videoSrc}
        poster={media.src}
        aria-label={media.alt || 'Video'}
        autoPlay={autoPlay}
        muted={muted}
        loop={loop}
        playsInline
        onClick={handleVideoClick}
        onError={handleError}
        onPlay={handlePlay}
        onPause={handlePause}
        onEnded={handleEnded}
      >
        {media.videoType && (
          <source src={media.videoSrc} type={media.videoType} />
        )}
      </video>

      {/* Play button overlay */}
      {!isPlaying && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/30">
          <button
            type="button"
            className="w-16 h-16 rounded-full bg-white/90 flex items-center justify-center shadow-lg hover:bg-white transition-colors"
            onClick={handlePlayPause}
            aria-label={labels.play}
          >
            <Play className="w-8 h-8 text-black ml-1" />
          </button>
        </div>
      )}

      {/* Controls overlay */}
      {showControls && showOverlay && isPlaying && (
        <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/60 to-transparent">
          <div className="flex items-center gap-3">
            <button
              type="button"
              className="p-2 rounded-full bg-white/20 hover:bg-white/30 text-white transition-colors"
              onClick={handlePlayPause}
              aria-label={isPlaying ? 'Pause' : 'Play'}
            >
              {isPlaying ? (
                <Pause className="w-5 h-5" />
              ) : (
                <Play className="w-5 h-5" />
              )}
            </button>

            <button
              type="button"
              className="p-2 rounded-full bg-white/20 hover:bg-white/30 text-white transition-colors"
              onClick={handleMuteToggle}
              aria-label={isMuted ? 'Unmute' : 'Mute'}
            >
              {isMuted ? (
                <VolumeX className="w-5 h-5" />
              ) : (
                <Volume2 className="w-5 h-5" />
              )}
            </button>

            <div className="flex-1" />

            <button
              type="button"
              className="p-2 rounded-full bg-white/20 hover:bg-white/30 text-white transition-colors"
              onClick={handleFullscreen}
              aria-label={labels.fullscreen}
            >
              <Maximize className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}

      {/* Video indicator badge */}
      <div className="absolute top-3 left-3 px-2 py-1 bg-black/60 rounded text-white text-xs font-medium">
        Video
      </div>
    </div>
  )
})

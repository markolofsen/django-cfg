/**
 * Professional VideoPlayer - Vidstack Implementation
 * Supports YouTube, Vimeo, MP4, HLS and more with custom controls
 */

'use client';

import React, { forwardRef, useImperativeHandle, useRef } from 'react';
import { MediaPlayer, MediaOutlet } from '@vidstack/react';
import { MediaRemoteControl, type MediaPlayerElement } from 'vidstack';
import { cn } from '@djangocfg/ui';
import { type VideoPlayerProps, type VideoPlayerRef } from './types';
import { VideoControls } from './VideoControls';

export const VideoPlayer = forwardRef<VideoPlayerRef, VideoPlayerProps>(({
  source,
  aspectRatio = 16 / 9,
  autoplay = false,
  muted = false,
  playsInline = true,
  controls = true,
  className,
  showInfo = false,
  theme = 'default',
  onPlay,
  onPause,
  onEnded,
  onError,
}, ref) => {
  const playerRef = useRef<MediaPlayerElement | null>(null);

  // Expose player methods via ref
  useImperativeHandle(ref, () => {
    const getRemote = () => {
      if (!playerRef.current) return null;
      const remote = new MediaRemoteControl();
      remote.setTarget(playerRef.current as unknown as EventTarget);
      return remote;
    };
    
    return {
      play: () => getRemote()?.play(),
      pause: () => getRemote()?.pause(),
      togglePlay: () => getRemote()?.togglePaused(),
      seekTo: (time: number) => getRemote()?.seek(time),
      setVolume: (volume: number) => getRemote()?.changeVolume(Math.max(0, Math.min(1, volume))),
      toggleMute: () => getRemote()?.toggleMuted(),
      enterFullscreen: () => getRemote()?.enterFullscreen(),
      exitFullscreen: () => getRemote()?.exitFullscreen(),
    };
  }, []);

  const handlePlay = () => {
    onPlay?.();
  };

  const handlePause = () => {
    onPause?.();
  };

  const handleEnded = () => {
    onEnded?.();
  };

  const handleError = (detail: any) => {
    onError?.(detail?.message || 'Video playback error');
  };

  return (
    <div className={cn("w-full", className)}>
      {/* Video Player */}
      <div 
        className={cn(
          "relative w-full overflow-hidden rounded-sm bg-black",
          theme === 'minimal' && "rounded-none",
          theme === 'modern' && "rounded-xl shadow-2xl"
        )}
        style={{ aspectRatio: aspectRatio }}
      >
        <MediaPlayer
          ref={playerRef}
          title={source.title || 'Video'}
          src={source.url}
          poster={source.poster}
          autoPlay={autoplay}
          muted={muted}
          playsInline={playsInline}
          onPlay={handlePlay}
          onPause={handlePause}
          onEnded={handleEnded}
          onError={handleError}
          className="w-full h-full"
        >
          <MediaOutlet />
          
          {/* Custom controls */}
          {controls && <VideoControls player={playerRef} />}
        </MediaPlayer>
      </div>
      
      {/* Video Info */}
      {showInfo && source.title && (
        <div className="mt-4 space-y-2">
          <h3 className="text-xl font-semibold text-foreground">{source.title}</h3>
          {source.description && (
            <p className="text-muted-foreground">{source.description}</p>
          )}
        </div>
      )}
    </div>
  );
});

VideoPlayer.displayName = 'VideoPlayer';

/**
 * Custom Video Controls for Vidstack Player
 */

'use client';

import React from 'react';
import { useMediaStore, useMediaRemote } from '@vidstack/react';
import type { MediaPlayerElement } from 'vidstack';
import { Play, Pause, Volume2, VolumeX, Maximize, Minimize } from 'lucide-react';
import { cn } from '@djangocfg/ui';

interface VideoControlsProps {
  player: React.RefObject<MediaPlayerElement | null>;
  className?: string;
}

export function VideoControls({ player, className }: VideoControlsProps) {
  const store = useMediaStore(player);
  const remote = useMediaRemote();
  
  const isPaused = store.paused;
  const isMuted = store.muted;
  const isFullscreen = store.fullscreen;
  const currentTime = store.currentTime;
  const duration = store.duration;
  const volume = store.volume;

  const formatTime = (seconds: number): string => {
    if (!seconds || seconds < 0) return '0:00';
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!duration) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const percentage = clickX / rect.width;
    const newTime = percentage * duration;
    remote.seek(newTime);
  };

  const handleVolumeChange = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const percentage = Math.max(0, Math.min(1, clickX / rect.width));
    remote.changeVolume(percentage);
    if (percentage > 0 && isMuted) {
      remote.toggleMuted();
    }
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className={cn(
      "absolute inset-0 flex flex-col justify-end opacity-0 hover:opacity-100 focus-within:opacity-100 transition-opacity duration-300",
      "bg-gradient-to-t from-black/80 via-black/20 to-transparent",
      className
    )}>
      {/* Progress Bar */}
      <div className="px-4 pb-2">
        <div 
          className="h-1.5 bg-white/20 rounded-full cursor-pointer hover:h-2 transition-all group"
          onClick={handleProgressClick}
        >
          <div 
            className="h-full bg-primary rounded-full transition-all relative group-hover:bg-primary/90"
            style={{ width: `${progress}%` }}
          >
            <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </div>
      </div>

      {/* Control Bar */}
      <div className="flex items-center gap-4 px-4 pb-4">
        {/* Play/Pause */}
        <button
          onClick={() => remote.togglePaused()}
          className="text-white hover:text-primary transition-colors p-1.5 hover:bg-white/10 rounded-full"
        >
          {isPaused ? <Play className="h-6 w-6" /> : <Pause className="h-6 w-6" />}
        </button>

        {/* Time */}
        <div className="text-white text-sm font-medium">
          {formatTime(currentTime)} / {formatTime(duration)}
        </div>

        <div className="flex-1" />

        {/* Volume Control */}
        <div className="flex items-center gap-2 group/volume">
          <button
            onClick={() => remote.toggleMuted()}
            className="text-white hover:text-primary transition-colors p-1.5 hover:bg-white/10 rounded-full"
          >
            {isMuted || volume === 0 ? (
              <VolumeX className="h-5 w-5" />
            ) : (
              <Volume2 className="h-5 w-5" />
            )}
          </button>
          
          <div 
            className="w-0 group-hover/volume:w-20 transition-all overflow-hidden"
          >
            <div 
              className="h-1.5 bg-white/20 rounded-full cursor-pointer hover:h-2 transition-all"
              onClick={handleVolumeChange}
            >
              <div 
                className="h-full bg-white rounded-full transition-all"
                style={{ width: `${volume * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Fullscreen */}
        <button
          onClick={() => isFullscreen ? remote.exitFullscreen() : remote.enterFullscreen()}
          className="text-white hover:text-primary transition-colors p-1.5 hover:bg-white/10 rounded-full"
        >
          {isFullscreen ? <Minimize className="h-5 w-5" /> : <Maximize className="h-5 w-5" />}
        </button>
      </div>
    </div>
  );
}

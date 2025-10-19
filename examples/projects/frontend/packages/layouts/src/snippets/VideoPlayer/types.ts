/**
 * VideoPlayer Types - Professional Vidstack Implementation
 */

export interface VideoSource {
  /** Video URL - supports YouTube, Vimeo, MP4, HLS, etc. */
  url: string;
  /** Video title */
  title?: string;
  /** Video description */
  description?: string;
  /** Custom poster/thumbnail URL */
  poster?: string;
  /** Video duration in seconds */
  duration?: number;
}

export interface VideoPlayerProps {
  /** Video source configuration */
  source: VideoSource;
  /** Aspect ratio (default: 16/9) */
  aspectRatio?: number;
  /** Auto-play video */
  autoplay?: boolean;
  /** Mute video by default */
  muted?: boolean;
  /** Play video inline on mobile */
  playsInline?: boolean;
  /** Show custom controls */
  controls?: boolean;
  /** Custom CSS class */
  className?: string;
  /** Show video info */
  showInfo?: boolean;
  /** Player theme */
  theme?: 'default' | 'minimal' | 'modern';
  /** Event callbacks */
  onPlay?: () => void;
  onPause?: () => void;
  onEnded?: () => void;
  onError?: (error: string) => void;
}

export interface VideoPlayerRef {
  /** Play video */
  play: () => void;
  /** Pause video */
  pause: () => void;
  /** Toggle play/pause */
  togglePlay: () => void;
  /** Seek to time */
  seekTo: (time: number) => void;
  /** Set volume (0-1) */
  setVolume: (volume: number) => void;
  /** Toggle mute */
  toggleMute: () => void;
  /** Enter fullscreen */
  enterFullscreen: () => void;
  /** Exit fullscreen */
  exitFullscreen: () => void;
}

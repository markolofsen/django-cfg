# VideoPlayer - Professional Vidstack Implementation

A professional, accessible video player built with Vidstack React that supports YouTube, Vimeo, MP4, HLS, and more.

## Features

- ✅ **Multi-platform support**: YouTube, Vimeo, MP4, HLS, DASH
- ✅ **Custom controls**: Professional UI with hover effects
- ✅ **Accessibility**: Full keyboard navigation and screen reader support
- ✅ **Responsive**: Works on all screen sizes
- ✅ **TypeScript**: Full type safety
- ✅ **Themes**: Default, minimal, and modern themes
- ✅ **No recommendations**: Clean playback without YouTube distractions

## Installation

The VideoPlayer is already included in the UI package with all dependencies:

```bash
pnpm add @vidstack/react@next media-icons@next
```

## Basic Usage

```tsx
import { VideoPlayer } from '@repo/ui/snippets/VideoPlayer';

function MyComponent() {
  return (
    <VideoPlayer
      source={{
        url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        title: 'Never Gonna Give You Up',
        description: 'Rick Astley - Never Gonna Give You Up (Official Video)'
      }}
      autoplay={false}
      controls={true}
      className="max-w-4xl mx-auto"
    />
  );
}
```

## Advanced Usage

```tsx
import { VideoPlayer, VideoPlayerRef } from '@repo/ui/snippets/VideoPlayer';
import { useRef } from 'react';

function AdvancedPlayer() {
  const playerRef = useRef<VideoPlayerRef>(null);

  const handleCustomPlay = () => {
    playerRef.current?.play();
  };

  return (
    <VideoPlayer
      ref={playerRef}
      source={{
        url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
        title: 'Big Buck Bunny',
        poster: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/BigBuckBunny.jpg',
        duration: 596
      }}
      theme="modern"
      autoplay={false}
      muted={false}
      playsInline={true}
      showInfo={true}
      onPlay={() => console.log('Video started')}
      onPause={() => console.log('Video paused')}
      onEnded={() => console.log('Video ended')}
      onError={(error) => console.error('Video error:', error)}
    />
  );
}
```

## Supported Video Sources

### YouTube
```tsx
<VideoPlayer
  source={{
    url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    title: 'YouTube Video'
  }}
/>
```

### Vimeo
```tsx
<VideoPlayer
  source={{
    url: 'https://vimeo.com/76979871',
    title: 'Vimeo Video'
  }}
/>
```

### Direct MP4
```tsx
<VideoPlayer
  source={{
    url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    title: 'Direct MP4',
    poster: 'https://example.com/poster.jpg'
  }}
/>
```

### HLS Stream
```tsx
<VideoPlayer
  source={{
    url: 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8',
    title: 'HLS Stream'
  }}
/>
```

## API Reference

### VideoPlayerProps

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `source` | `VideoSource` | - | Video source configuration |
| `aspectRatio` | `number` | `16/9` | Video aspect ratio |
| `autoplay` | `boolean` | `false` | Auto-play video |
| `muted` | `boolean` | `false` | Mute video by default |
| `playsInline` | `boolean` | `true` | Play inline on mobile |
| `controls` | `boolean` | `true` | Show custom controls |
| `showInfo` | `boolean` | `false` | Show video info below player |
| `theme` | `'default' \| 'minimal' \| 'modern'` | `'default'` | Player theme |
| `className` | `string` | - | Custom CSS class |
| `onPlay` | `() => void` | - | Play event callback |
| `onPause` | `() => void` | - | Pause event callback |
| `onEnded` | `() => void` | - | End event callback |
| `onError` | `(error: string) => void` | - | Error event callback |

### VideoSource

| Property | Type | Description |
|----------|------|-------------|
| `url` | `string` | Video URL (YouTube, Vimeo, MP4, HLS, etc.) |
| `title` | `string?` | Video title |
| `description` | `string?` | Video description |
| `poster` | `string?` | Custom poster/thumbnail URL |
| `duration` | `number?` | Video duration in seconds |

### VideoPlayerRef Methods

| Method | Description |
|--------|-------------|
| `play()` | Play the video |
| `pause()` | Pause the video |
| `togglePlay()` | Toggle play/pause |
| `seekTo(time: number)` | Seek to specific time |
| `setVolume(volume: number)` | Set volume (0-1) |
| `toggleMute()` | Toggle mute |
| `enterFullscreen()` | Enter fullscreen |
| `exitFullscreen()` | Exit fullscreen |

## Themes

### Default Theme
Clean, professional look with rounded corners and subtle shadows.

### Minimal Theme
No rounded corners, minimal styling for embedding in tight spaces.

### Modern Theme
Enhanced shadows and larger border radius for a contemporary look.

## Accessibility

The VideoPlayer includes full accessibility support:

- ✅ Keyboard navigation (Space, Arrow keys, F for fullscreen)
- ✅ Screen reader announcements
- ✅ Focus indicators
- ✅ ARIA labels and roles
- ✅ High contrast support

## Performance

- ✅ Lazy loading of video content
- ✅ Efficient re-renders with Vidstack's optimized state management
- ✅ Minimal bundle size impact
- ✅ Hardware-accelerated playback when available

## Browser Support

Supports all modern browsers through Vidstack's comprehensive compatibility layer:

- ✅ Chrome 63+
- ✅ Firefox 67+
- ✅ Safari 12+
- ✅ Edge 79+
- ✅ iOS Safari 12+
- ✅ Chrome Android 63+

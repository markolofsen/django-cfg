'use client';

import { useEffect } from 'react';
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { useShallow } from 'zustand/react/shallow';

import { createLogger } from '@djangocfg/ui-core/lib';

const cacheDebug = createLogger('MediaCache');

// Types
interface BlobUrlEntry {
  url: string;
  refCount: number;
  createdAt: number;
}

interface ImageDimensions {
  width: number;
  height: number;
}

interface VideoMetadata {
  duration: number;
  width: number;
  height: number;
  codec?: string;
}

interface EffectConfig {
  opacity: number;
  scale: number;
  blur: string;
}

/** Video player settings (persisted) */
interface VideoPlayerSettings {
  volume: number;
  isLooping: boolean;
}

// Stream URL TTL (30 seconds - shorter to avoid stale session/token issues)
const STREAM_URL_TTL = 30 * 1000;

interface MediaCacheState {
  // Blob URL cache (shared by Image, Audio, Video)
  blobUrls: Map<string, BlobUrlEntry>;

  // Image-specific
  imageDimensions: Map<string, ImageDimensions>;

  // Audio-specific
  audioPlaybackPositions: Map<string, number>;
  audioEffectConfigs: Map<string, EffectConfig>;

  // Video-specific
  videoStreamUrls: Map<string, { url: string; timestamp: number }>;
  videoPosterUrls: Map<string, string>;
  videoPlaybackPositions: Map<string, number>;
  videoMetadata: Map<string, VideoMetadata>;
  videoPlayerSettings: VideoPlayerSettings;
}

interface MediaCacheActions {
  // Blob URL management (shared)
  getOrCreateBlobUrl: (
    key: string,
    content: ArrayBuffer,
    mimeType: string
  ) => string;
  releaseBlobUrl: (key: string) => void;
  hasBlobUrl: (key: string) => boolean;

  // Image actions
  cacheDimensions: (src: string, dims: ImageDimensions) => void;
  getDimensions: (src: string) => ImageDimensions | null;

  // Audio actions
  saveAudioPosition: (uri: string, time: number) => void;
  getAudioPosition: (uri: string) => number | null;
  getEffectConfig: (key: string) => EffectConfig | null;
  cacheEffectConfig: (key: string, config: EffectConfig) => void;

  // Video actions
  getOrCreateStreamUrl: (
    sessionId: string,
    path: string,
    generator: (sessionId: string, path: string) => string
  ) => string;
  getPosterUrl: (title: string) => string | null;
  cachePosterUrl: (title: string, url: string) => void;
  saveVideoPosition: (key: string, time: number) => void;
  getVideoPosition: (key: string) => number | null;
  cacheVideoMetadata: (url: string, meta: VideoMetadata) => void;
  getVideoMetadata: (url: string) => VideoMetadata | null;
  invalidateSession: (sessionId: string) => void;
  getVideoPlayerSettings: () => VideoPlayerSettings;
  saveVideoPlayerSettings: (settings: Partial<VideoPlayerSettings>) => void;

  // Global
  clearCache: () => void;
  getCacheStats: () => {
    blobUrls: number;
    dimensions: number;
    audioPositions: number;
    videoPositions: number;
  };
}

type MediaCacheStore = MediaCacheState & MediaCacheActions;

// Initial state
const DEFAULT_VIDEO_SETTINGS: VideoPlayerSettings = {
  volume: 1,
  isLooping: false,
};

const initialState: MediaCacheState = {
  blobUrls: new Map(),
  imageDimensions: new Map(),
  audioPlaybackPositions: new Map(),
  audioEffectConfigs: new Map(),
  videoStreamUrls: new Map(),
  videoPosterUrls: new Map(),
  videoPlaybackPositions: new Map(),
  videoMetadata: new Map(),
  videoPlayerSettings: DEFAULT_VIDEO_SETTINGS,
};

export const useMediaCacheStore = create<MediaCacheStore>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // ========== Blob URL Management ==========

        getOrCreateBlobUrl: (key, content, mimeType) => {
          const existing = get().blobUrls.get(key);
          if (existing) {
            // Increment ref count
            cacheDebug.debug(`Blob URL reused: ${key}`, { refCount: existing.refCount + 1 });
            set(
              (state) => ({
                blobUrls: new Map(state.blobUrls).set(key, {
                  ...existing,
                  refCount: existing.refCount + 1,
                }),
              }),
              false,
              'blobUrl/incrementRef'
            );
            return existing.url;
          }

          // Create new blob URL
          const blob = new Blob([content], { type: mimeType });
          const url = URL.createObjectURL(blob);
          const sizeMB = (content.byteLength / 1024 / 1024).toFixed(2);
          cacheDebug.debug(`Blob URL created: ${key}`, { mimeType, size: `${sizeMB}MB` });
          set(
            (state) => ({
              blobUrls: new Map(state.blobUrls).set(key, {
                url,
                refCount: 1,
                createdAt: Date.now(),
              }),
            }),
            false,
            'blobUrl/create'
          );
          return url;
        },

        releaseBlobUrl: (key) => {
          const entry = get().blobUrls.get(key);
          if (!entry) return;

          if (entry.refCount <= 1) {
            // Last reference - revoke and remove
            cacheDebug.debug(`Blob URL revoked: ${key}`);
            URL.revokeObjectURL(entry.url);
            set(
              (state) => {
                const newMap = new Map(state.blobUrls);
                newMap.delete(key);
                return { blobUrls: newMap };
              },
              false,
              'blobUrl/revoke'
            );
          } else {
            // Decrement ref count
            cacheDebug.debug(`Blob URL released: ${key}`, { refCount: entry.refCount - 1 });
            set(
              (state) => ({
                blobUrls: new Map(state.blobUrls).set(key, {
                  ...entry,
                  refCount: entry.refCount - 1,
                }),
              }),
              false,
              'blobUrl/decrementRef'
            );
          }
        },

        hasBlobUrl: (key) => get().blobUrls.has(key),

        // ========== Image Cache ==========

        cacheDimensions: (src, dims) => {
          set(
            (state) => ({
              imageDimensions: new Map(state.imageDimensions).set(src, dims),
            }),
            false,
            'image/cacheDimensions'
          );
        },

        getDimensions: (src) => get().imageDimensions.get(src) ?? null,

        // ========== Audio Cache ==========

        saveAudioPosition: (uri, time) => {
          set(
            (state) => ({
              audioPlaybackPositions: new Map(state.audioPlaybackPositions).set(
                uri,
                time
              ),
            }),
            false,
            'audio/savePosition'
          );
        },

        getAudioPosition: (uri) =>
          get().audioPlaybackPositions.get(uri) ?? null,

        getEffectConfig: (key) => get().audioEffectConfigs.get(key) ?? null,

        cacheEffectConfig: (key, config) => {
          set(
            (state) => ({
              audioEffectConfigs: new Map(state.audioEffectConfigs).set(
                key,
                config
              ),
            }),
            false,
            'audio/cacheEffectConfig'
          );
        },

        // ========== Video Cache ==========

        getOrCreateStreamUrl: (sessionId, path, generator) => {
          const key = `${sessionId}:${path}`;
          const cached = get().videoStreamUrls.get(key);

          // Return if fresh
          if (cached && Date.now() - cached.timestamp < STREAM_URL_TTL) {
            return cached.url;
          }

          // Generate and cache
          const url = generator(sessionId, path);
          set(
            (state) => ({
              videoStreamUrls: new Map(state.videoStreamUrls).set(key, {
                url,
                timestamp: Date.now(),
              }),
            }),
            false,
            'video/cacheStreamUrl'
          );
          return url;
        },

        getPosterUrl: (title) => get().videoPosterUrls.get(title) ?? null,

        cachePosterUrl: (title, url) => {
          set(
            (state) => ({
              videoPosterUrls: new Map(state.videoPosterUrls).set(title, url),
            }),
            false,
            'video/cachePosterUrl'
          );
        },

        saveVideoPosition: (key, time) => {
          set(
            (state) => ({
              videoPlaybackPositions: new Map(state.videoPlaybackPositions).set(
                key,
                time
              ),
            }),
            false,
            'video/savePosition'
          );
        },

        getVideoPosition: (key) =>
          get().videoPlaybackPositions.get(key) ?? null,

        cacheVideoMetadata: (url, meta) => {
          set(
            (state) => ({
              videoMetadata: new Map(state.videoMetadata).set(url, meta),
            }),
            false,
            'video/cacheMetadata'
          );
        },

        getVideoMetadata: (url) => get().videoMetadata.get(url) ?? null,

        invalidateSession: (sessionId) => {
          set(
            (state) => {
              const newUrls = new Map(state.videoStreamUrls);
              for (const [key] of newUrls) {
                if (key.startsWith(`${sessionId}:`)) {
                  newUrls.delete(key);
                }
              }
              return { videoStreamUrls: newUrls };
            },
            false,
            'video/invalidateSession'
          );
        },

        getVideoPlayerSettings: () => get().videoPlayerSettings,

        saveVideoPlayerSettings: (settings) => {
          set(
            (state) => ({
              videoPlayerSettings: { ...state.videoPlayerSettings, ...settings },
            }),
            false,
            'video/savePlayerSettings'
          );
        },

        // ========== Global ==========

        clearCache: () => {
          const stats = get().getCacheStats();
          cacheDebug.info('Clearing cache', stats);
          // Revoke all blob URLs before clearing
          get().blobUrls.forEach(({ url }) => URL.revokeObjectURL(url));
          set(initialState, false, 'clearCache');
        },

        getCacheStats: () => ({
          blobUrls: get().blobUrls.size,
          dimensions: get().imageDimensions.size,
          audioPositions: get().audioPlaybackPositions.size,
          videoPositions: get().videoPlaybackPositions.size,
        }),
      }),
      {
        name: 'media-cache-storage',
        // Only persist playback positions, poster URLs, and player settings
        partialize: (state) => ({
          audioPlaybackPositions: Array.from(
            state.audioPlaybackPositions.entries()
          ),
          videoPlaybackPositions: Array.from(
            state.videoPlaybackPositions.entries()
          ),
          videoPosterUrls: Array.from(state.videoPosterUrls.entries()),
          videoPlayerSettings: state.videoPlayerSettings,
        }),
        // Rehydrate Maps from arrays
        onRehydrateStorage: () => (state) => {
          if (state) {
            // Type assertion for persisted data
            const persistedAudio = state.audioPlaybackPositions as unknown;
            const persistedVideo = state.videoPlaybackPositions as unknown;
            const persistedPosters = state.videoPosterUrls as unknown;
            const persistedSettings = state.videoPlayerSettings as unknown;

            state.audioPlaybackPositions = new Map(
              Array.isArray(persistedAudio)
                ? (persistedAudio as [string, number][])
                : []
            );
            state.videoPlaybackPositions = new Map(
              Array.isArray(persistedVideo)
                ? (persistedVideo as [string, number][])
                : []
            );
            state.videoPosterUrls = new Map(
              Array.isArray(persistedPosters)
                ? (persistedPosters as [string, string][])
                : []
            );
            // Merge persisted settings with defaults (handles missing fields)
            state.videoPlayerSettings = {
              ...DEFAULT_VIDEO_SETTINGS,
              ...(persistedSettings && typeof persistedSettings === 'object'
                ? (persistedSettings as Partial<VideoPlayerSettings>)
                : {}),
            };
          }
        },
      }
    ),
    { name: 'MediaCacheStore' }
  )
);

// ========== Selective Hooks ==========

/**
 * Hook for image-related cache operations
 * Uses useShallow to prevent infinite re-renders
 */
export const useImageCache = () =>
  useMediaCacheStore(
    useShallow((state) => ({
      getOrCreateBlobUrl: state.getOrCreateBlobUrl,
      releaseBlobUrl: state.releaseBlobUrl,
      hasBlobUrl: state.hasBlobUrl,
      cacheDimensions: state.cacheDimensions,
      getDimensions: state.getDimensions,
    }))
  );

/**
 * Hook for audio-related cache operations
 * Uses useShallow to prevent infinite re-renders
 */
export const useAudioCache = () =>
  useMediaCacheStore(
    useShallow((state) => ({
      getOrCreateBlobUrl: state.getOrCreateBlobUrl,
      releaseBlobUrl: state.releaseBlobUrl,
      hasBlobUrl: state.hasBlobUrl,
      saveAudioPosition: state.saveAudioPosition,
      getAudioPosition: state.getAudioPosition,
      getEffectConfig: state.getEffectConfig,
      cacheEffectConfig: state.cacheEffectConfig,
    }))
  );

/**
 * Hook for video-related cache operations
 * Uses useShallow to prevent infinite re-renders
 */
export const useVideoCache = () =>
  useMediaCacheStore(
    useShallow((state) => ({
      getOrCreateBlobUrl: state.getOrCreateBlobUrl,
      releaseBlobUrl: state.releaseBlobUrl,
      hasBlobUrl: state.hasBlobUrl,
      getOrCreateStreamUrl: state.getOrCreateStreamUrl,
      getPosterUrl: state.getPosterUrl,
      cachePosterUrl: state.cachePosterUrl,
      saveVideoPosition: state.saveVideoPosition,
      getVideoPosition: state.getVideoPosition,
      cacheVideoMetadata: state.cacheVideoMetadata,
      getVideoMetadata: state.getVideoMetadata,
      invalidateSession: state.invalidateSession,
      getVideoPlayerSettings: state.getVideoPlayerSettings,
      saveVideoPlayerSettings: state.saveVideoPlayerSettings,
    }))
  );

/**
 * Hook for video player settings only
 * Returns current settings and save function
 */
export const useVideoPlayerSettings = () =>
  useMediaCacheStore(
    useShallow((state) => ({
      settings: state.videoPlayerSettings,
      saveSettings: state.saveVideoPlayerSettings,
    }))
  );

/**
 * Hook for blob URL cleanup on unmount
 */
export function useBlobUrlCleanup(key: string | null) {
  const releaseBlobUrl = useMediaCacheStore((s) => s.releaseBlobUrl);

  // useEffect must run unconditionally — the previous `if (typeof window ...)`
  // guard plus a render-time `require('react')` meant the hook ran on the
  // client but not on the server, so the hook count differed between the SSR
  // and hydration renders (rules-of-hooks / #310). The effect is a no-op on the
  // server anyway (effects never run there), and the `key` null-check below
  // already handles the "nothing to release" case.
  useEffect(() => {
    return () => {
      if (key) {
        releaseBlobUrl(key);
      }
    };
  }, [key, releaseBlobUrl]);
}

// ========== Utilities ==========

/**
 * Generate a cache key from ArrayBuffer content
 * Uses first and last 1KB + length for fast hashing
 */
export function generateContentKey(content: ArrayBuffer): string {
  const arr = new Uint8Array(content);
  const len = arr.length;

  // Take first 1KB
  const start = arr.slice(0, Math.min(1024, len));
  // Take last 1KB
  const end = arr.slice(Math.max(0, len - 1024));

  // Simple hash from bytes. `for..of` over a Uint8Array yields `number`;
  // indexing it yields `number | undefined` under noUncheckedIndexedAccess.
  let hash = len;
  for (const byte of start) {
    hash = ((hash << 5) - hash + byte) | 0;
  }
  for (const byte of end) {
    hash = ((hash << 5) - hash + byte) | 0;
  }

  return `blob-${len}-${hash.toString(16)}`;
}

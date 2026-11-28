'use client';

/**
 * useImageLoading - Manages image loading state with LQIP
 */

import { useEffect, useRef, useState } from 'react';

import { generateContentKey, useMediaCacheStore } from '../../internal/media-cache';
import {
    createLQIP, imageDebug, MAX_IMAGE_SIZE, PROGRESSIVE_LOADING_THRESHOLD, WARNING_IMAGE_SIZE
} from '../utils';

// =============================================================================
// TYPES
// =============================================================================

export interface UseImageLoadingOptions {
  /** Image content (ArrayBuffer or string) */
  content: string | ArrayBuffer;
  /** MIME type for blob creation */
  mimeType?: string;
  /**
   * Direct image URL (bypasses content→blob conversion).
   * When provided, content is ignored and URL is used directly.
   */
  src?: string;
}

export interface UseImageLoadingReturn {
  /** Blob URL source for the image */
  src: string | null;
  /** Low-quality placeholder URL */
  lqip: string | null;
  /** Whether full image is loaded */
  isFullyLoaded: boolean;
  /** Whether to use progressive loading */
  useProgressiveLoading: boolean;
  /** Error message if any */
  error: string | null;
  /** Content key for caching */
  contentKey: string | null;
  /** Image size in bytes */
  size: number;
  /** Whether content exists */
  hasContent: boolean;
}

// =============================================================================
// HOOK
// =============================================================================

export function useImageLoading(options: UseImageLoadingOptions): UseImageLoadingReturn {
  const { content, mimeType, src: directSrc } = options;

  // Get stable function references from store (not from hook to avoid re-renders)
  const getOrCreateBlobUrl = useMediaCacheStore.getState().getOrCreateBlobUrl;
  const releaseBlobUrl = useMediaCacheStore.getState().releaseBlobUrl;

  const [src, setSrc] = useState<string | null>(null);
  const [lqip, setLqip] = useState<string | null>(null);
  const [isFullyLoaded, setIsFullyLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const contentKeyRef = useRef<string | null>(null);
  const isMountedRef = useRef(true);

  // Calculate size and flags
  const size = content ? (typeof content === 'string' ? content.length : content.byteLength) : 0;
  // When directSrc is provided, we have content (the URL itself)
  const hasContent = directSrc ? true : size > 0;
  const useProgressiveLoading = directSrc ? false : size > PROGRESSIVE_LOADING_THRESHOLD;

  // Track unmount for cleanup
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
      // Release blob URL only on actual unmount
      if (contentKeyRef.current) {
        useMediaCacheStore.getState().releaseBlobUrl(contentKeyRef.current);
        contentKeyRef.current = null;
      }
    };
  }, []);

  // Create blob URL with caching and size validation
  useEffect(() => {
    // Reset error state
    setError(null);

    // Direct URL mode - use as-is without blob conversion
    if (directSrc) {
      imageDebug.load(directSrc, 'url');
      setSrc(directSrc);
      setIsFullyLoaded(true);
      return;
    }

    if (!hasContent) {
      setSrc(null);
      return;
    }

    // Size validation - reject oversized images
    if (size > MAX_IMAGE_SIZE) {
      const sizeMB = (size / 1024 / 1024).toFixed(1);
      const errorMsg = `Image too large: ${sizeMB}MB (maximum: 50MB)`;
      imageDebug.error(errorMsg, { size, sizeMB, maxSize: MAX_IMAGE_SIZE });
      setError(errorMsg);
      setSrc(null);
      return;
    }

    // Warn about large images
    if (size > WARNING_IMAGE_SIZE) {
      const sizeMB = (size / 1024 / 1024).toFixed(1);
      imageDebug.warn(`Large image: ${sizeMB}MB - may impact performance`);
    }

    // Handle string content (data URLs or binary strings)
    if (typeof content === 'string') {
      // Pass through data URLs directly
      if (content.startsWith('data:')) {
        imageDebug.load(content.slice(0, 50) + '...', 'data-url');
        setSrc(content);
        return;
      }

      // Convert binary string to ArrayBuffer and use Blob URL
      const encoder = new TextEncoder();
      const buffer = encoder.encode(content).buffer;
      const contentKey = generateContentKey(buffer);

      // Release previous blob URL if content changed
      if (contentKeyRef.current && contentKeyRef.current !== contentKey) {
        releaseBlobUrl(contentKeyRef.current);
      }

      contentKeyRef.current = contentKey;
      const url = getOrCreateBlobUrl(contentKey, buffer, mimeType || 'image/png');
      imageDebug.load(url, 'blob');
      imageDebug.state('loaded', { size, mimeType, contentKey });
      setSrc(url);
      return;
    }

    // Handle ArrayBuffer with cached blob URL
    const contentKey = generateContentKey(content);

    // Release previous blob URL if content changed
    if (contentKeyRef.current && contentKeyRef.current !== contentKey) {
      releaseBlobUrl(contentKeyRef.current);
    }

    contentKeyRef.current = contentKey;
    const url = getOrCreateBlobUrl(contentKey, content, mimeType || 'image/png');
    imageDebug.load(url, 'blob');
    imageDebug.state('loaded', { size, mimeType, contentKey });
    setSrc(url);

    // No cleanup here - cleanup happens in unmount effect above
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [content, mimeType, hasContent, size, directSrc]);

  // Create LQIP for progressive loading
  useEffect(() => {
    if (!src || !useProgressiveLoading) {
      setLqip(null);
      setIsFullyLoaded(true);
      return;
    }

    setLqip(null);
    setIsFullyLoaded(false);
    imageDebug.state('progressive loading', { size });

    // Guard against state updates after src change / unmount
    let cancelled = false;

    // Create low-quality placeholder
    createLQIP(src).then((placeholder) => {
      if (cancelled || !isMountedRef.current) return;
      if (placeholder) {
        imageDebug.debug('LQIP created');
        setLqip(placeholder);
      }
    });

    // Pre-load full image
    const img = new Image();
    img.onload = () => {
      if (cancelled || !isMountedRef.current) return;
      imageDebug.state('fully loaded');
      setIsFullyLoaded(true);
    };
    img.onerror = () => {
      imageDebug.error('Failed to load full image');
    };
    img.src = src;

    return () => {
      cancelled = true;
      img.onload = null;
      img.onerror = null;
      img.src = '';
    };
  }, [src, useProgressiveLoading, size]);

  return {
    src,
    lqip,
    isFullyLoaded,
    useProgressiveLoading,
    error,
    contentKey: contentKeyRef.current,
    size,
    hasContent,
  };
}

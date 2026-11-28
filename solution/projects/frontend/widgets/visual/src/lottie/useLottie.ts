/**
 * useLottie Hook
 *
 * Hook for loading and managing Lottie animation data
 */

'use client';

import { useEffect, useRef, useState } from 'react';

export interface UseLottieOptions {
  /**
   * Animation data (JSON object) or URL to load from
   */
  src: string | object;

  /**
   * Enable caching of loaded animations
   * @default true
   */
  cache?: boolean;
}

export interface UseLottieReturn {
  /**
   * Loaded animation data
   */
  animationData: object | null;

  /**
   * Loading state
   */
  isLoading: boolean;

  /**
   * Error state
   */
  error: Error | null;

  /**
   * Retry loading the animation
   */
  retry: () => void;
}

// Simple in-memory cache for loaded animations
const animationCache = new Map<string, object>();

/**
 * Hook for loading Lottie animations from URLs or objects
 *
 * Features:
 * - Loads animations from URLs or accepts animation objects directly
 * - Caching support to prevent re-fetching the same animation
 * - Aborts in-flight requests on unmount / src change
 * - Error handling with retry capability
 * - Loading states
 *
 * Usage:
 * ```tsx
 * const { animationData, isLoading, error, retry } = useLottie({
 *   src: 'https://example.com/animation.json'
 * });
 *
 * if (isLoading) return <div>Loading...</div>;
 * if (error) return <div>Error: {error.message} <button onClick={retry}>Retry</button></div>;
 * if (!animationData) return null;
 *
 * return <LottiePlayer animationData={animationData} />;
 * ```
 */
export function useLottie(options: UseLottieOptions): UseLottieReturn {
  const { src, cache = true } = options;

  const [animationData, setAnimationData] = useState<object | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  // Track if component is mounted to prevent state updates on unmounted component
  const isMountedRef = useRef(true);

  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    // If src is already an object, use it directly.
    // Only update state when the reference actually changes so that
    // callers passing an inline object literal do not trigger an
    // infinite render loop.
    if (typeof src === 'object' && src !== null) {
      setAnimationData((prev) => (prev === src ? prev : src));
      setIsLoading(false);
      setError(null);
      return;
    }

    // If src is a string (URL), fetch it
    if (typeof src === 'string') {
      const abortController = new AbortController();

      const loadAnimation = async () => {
        // Check cache first
        if (cache && animationCache.has(src)) {
          if (isMountedRef.current) {
            setAnimationData(animationCache.get(src)!);
            setIsLoading(false);
            setError(null);
          }
          return;
        }

        // Load from URL
        if (isMountedRef.current) {
          setIsLoading(true);
          setError(null);
        }

        try {
          const response = await fetch(src, { signal: abortController.signal });

          if (!response.ok) {
            throw new Error(`Failed to load animation: ${response.status} ${response.statusText}`);
          }

          let data: unknown;
          try {
            data = await response.json();
          } catch {
            throw new Error('Animation file is not valid JSON');
          }

          // Validate that it's a valid Lottie animation
          if (
            !data ||
            typeof data !== 'object' ||
            !('v' in data) ||
            !('layers' in data) ||
            !Array.isArray((data as { layers: unknown }).layers)
          ) {
            throw new Error('Invalid Lottie animation data');
          }

          // Cache the loaded animation
          if (cache) {
            animationCache.set(src, data as object);
          }

          if (isMountedRef.current) {
            setAnimationData(data as object);
            setIsLoading(false);
          }
        } catch (err) {
          // Ignore aborts triggered by unmount / src change.
          if (abortController.signal.aborted) {
            return;
          }
          if (isMountedRef.current) {
            setError(err instanceof Error ? err : new Error('Failed to load animation'));
            setIsLoading(false);
          }
        }
      };

      loadAnimation();

      return () => {
        abortController.abort();
      };
    }
  }, [src, cache, retryCount]);

  const retry = () => {
    setRetryCount((prev) => prev + 1);
  };

  return {
    animationData,
    isLoading,
    error,
    retry,
  };
}

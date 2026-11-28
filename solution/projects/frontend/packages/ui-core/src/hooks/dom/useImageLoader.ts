/**
 * Enhanced Image Loader Hook
 * 
 * Hook to check if an image is loaded successfully with callback support
 */

'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

export interface ImageLoaderState {
  isLoading: boolean;
  isLoaded: boolean;
  hasError: boolean;
}

export interface ImageLoaderCallbacks {
  onLoadStart?: () => void;
  /**
   * Receives the DOM `Event` from a detached `new Image()`, NOT a React
   * synthetic event: there is no React element behind this load, so
   * `persist`, `nativeEvent` and `isDefaultPrevented` do not exist on it.
   */
  onLoad?: (event: Event) => void;
  onError?: (event: Event) => void;
}

export const useImageLoader = (
  src?: string, 
  callbacks?: ImageLoaderCallbacks
): ImageLoaderState => {
  const [state, setState] = useState<ImageLoaderState>({
    isLoading: false,
    isLoaded: false,
    hasError: false,
  });

  // Callbacks are read through a ref so they never participate in the deps
  // below. Callers pass `callbacks` as an inline object literal, so depending on
  // it would re-run the load effect on every render — refetching the image and
  // re-firing onLoadStart indefinitely. The ref keeps the latest handlers
  // without tying image loading to render identity.
  const callbacksRef = useRef(callbacks);
  callbacksRef.current = callbacks;

  const handleLoad = useCallback((event: Event) => {
    setState({
      isLoading: false,
      isLoaded: true,
      hasError: false,
    });

    callbacksRef.current?.onLoad?.(event);
  }, []);

  const handleError = useCallback((event: Event) => {
    setState({
      isLoading: false,
      isLoaded: false,
      hasError: true,
    });

    callbacksRef.current?.onError?.(event);
  }, []);

  useEffect(() => {
    if (!src) {
      setState({
        isLoading: false,
        isLoaded: false,
        hasError: true,
      });
      return;
    }

    setState({
      isLoading: true,
      isLoaded: false,
      hasError: false,
    });

    callbacksRef.current?.onLoadStart?.();

    const img = new Image();
    
    img.addEventListener('load', handleLoad);
    img.addEventListener('error', handleError);
    
    img.src = src;

    // Cleanup function
    return () => {
      img.removeEventListener('load', handleLoad);
      img.removeEventListener('error', handleError);
    };
  }, [src, handleLoad, handleError]);

  return state;
};

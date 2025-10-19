/**
 * Enhanced Image Loader Hook
 * 
 * Hook to check if an image is loaded successfully with callback support
 */

import { useState, useEffect, useCallback } from 'react';

export interface ImageLoaderState {
  isLoading: boolean;
  isLoaded: boolean;
  hasError: boolean;
}

export interface ImageLoaderCallbacks {
  onLoadStart?: () => void;
  onLoad?: (event: React.SyntheticEvent<HTMLImageElement>) => void;
  onError?: (event: React.SyntheticEvent<HTMLImageElement>) => void;
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

  const handleLoad = useCallback((event: Event) => {
    setState({
      isLoading: false,
      isLoaded: true,
      hasError: false,
    });
    
    // Call user callback if provided
    if (callbacks?.onLoad) {
      callbacks.onLoad(event as unknown as React.SyntheticEvent<HTMLImageElement>);
    }
  }, [callbacks?.onLoad]);

  const handleError = useCallback((event: Event) => {
    setState({
      isLoading: false,
      isLoaded: false,
      hasError: true,
    });
    
    // Call user callback if provided
    if (callbacks?.onError) {
      callbacks.onError(event as unknown as React.SyntheticEvent<HTMLImageElement>);
    }
  }, [callbacks?.onError]);

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

    // Call load start callback
    if (callbacks?.onLoadStart) {
      callbacks.onLoadStart();
    }

    const img = new Image();
    
    img.addEventListener('load', handleLoad);
    img.addEventListener('error', handleError);
    
    img.src = src;

    // Cleanup function
    return () => {
      img.removeEventListener('load', handleLoad);
      img.removeEventListener('error', handleError);
    };
  }, [src, handleLoad, handleError, callbacks?.onLoadStart]);

  return state;
};

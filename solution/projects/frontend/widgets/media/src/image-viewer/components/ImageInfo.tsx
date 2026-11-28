'use client';

/**
 * ImageInfo - Displays image dimensions badge
 */

import { useEffect, useState } from 'react';
import { useImageCache } from '../../internal/media-cache';
import type { ImageInfoProps } from '../types';

// =============================================================================
// COMPONENT
// =============================================================================

export function ImageInfo({ src }: ImageInfoProps) {
  const { getDimensions, cacheDimensions } = useImageCache();
  const [dimensions, setDimensions] = useState<{ w: number; h: number } | null>(null);

  useEffect(() => {
    // Check cache first
    const cached = getDimensions(src);
    if (cached) {
      setDimensions({ w: cached.width, h: cached.height });
      return;
    }

    // Clear stale dimensions while the new source resolves
    setDimensions(null);

    // Load and cache dimensions
    let cancelled = false;
    const img = new Image();
    img.onload = () => {
      if (cancelled) return;
      const dims = { w: img.naturalWidth, h: img.naturalHeight };
      setDimensions(dims);
      cacheDimensions(src, { width: dims.w, height: dims.h });
    };
    img.src = src;

    return () => {
      cancelled = true;
      img.onload = null;
      img.src = '';
    };
  }, [src, getDimensions, cacheDimensions]);

  if (!dimensions) return null;

  return (
    <div className="absolute top-3 right-3 z-10 px-2 py-1 bg-black/60 backdrop-blur-sm border border-white/10 rounded text-[10px] text-white/80 font-mono">
      {dimensions.w} × {dimensions.h}
    </div>
  );
}

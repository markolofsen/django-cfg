'use client';

/**
 * useImageTransform - Manages image rotation and flip state
 */

import { useCallback, useEffect, useMemo, useState } from 'react';

import { DEFAULT_TRANSFORM } from '../utils';

import type { ImageTransform } from '../types';
// =============================================================================
// TYPES
// =============================================================================

export interface UseImageTransformOptions {
  /** Reset transform when this key changes */
  resetKey?: string;
}

export interface UseImageTransformReturn {
  /** Current transform state */
  transform: ImageTransform;
  /** Rotate 90 degrees clockwise */
  rotate: () => void;
  /** Toggle horizontal flip */
  flipH: () => void;
  /** Toggle vertical flip */
  flipV: () => void;
  /** Reset all transforms */
  reset: () => void;
  /** CSS transform string for applying to image */
  transformStyle: string;
}

// =============================================================================
// HOOK
// =============================================================================

export function useImageTransform(
  options: UseImageTransformOptions = {}
): UseImageTransformReturn {
  const { resetKey } = options;

  const [transform, setTransform] = useState<ImageTransform>(DEFAULT_TRANSFORM);

  // Reset transform when key changes
  useEffect(() => {
    setTransform(DEFAULT_TRANSFORM);
  }, [resetKey]);

  const rotate = useCallback(() => {
    setTransform((prev) => ({
      ...prev,
      rotation: (prev.rotation + 90) % 360,
    }));
  }, []);

  const flipH = useCallback(() => {
    setTransform((prev) => ({
      ...prev,
      flipH: !prev.flipH,
    }));
  }, []);

  const flipV = useCallback(() => {
    setTransform((prev) => ({
      ...prev,
      flipV: !prev.flipV,
    }));
  }, []);

  const reset = useCallback(() => {
    setTransform(DEFAULT_TRANSFORM);
  }, []);

  // Build CSS transform string
  const transformStyle = useMemo(() => {
    const transforms: string[] = [];

    if (transform.rotation !== 0) {
      transforms.push(`rotate(${transform.rotation}deg)`);
    }
    if (transform.flipH) {
      transforms.push('scaleX(-1)');
    }
    if (transform.flipV) {
      transforms.push('scaleY(-1)');
    }

    return transforms.join(' ') || 'none';
  }, [transform]);

  return {
    transform,
    rotate,
    flipH,
    flipV,
    reset,
    transformStyle,
  };
}

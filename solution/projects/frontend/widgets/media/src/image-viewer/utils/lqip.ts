/**
 * LQIP (Low-Quality Image Placeholder) generator
 *
 * Creates a tiny blurred preview image for progressive loading.
 */

import { LQIP_QUALITY, LQIP_SIZE } from './constants';

/**
 * Create a low-quality image placeholder from source URL
 *
 * @param imageSrc - Full quality image URL
 * @returns Data URL of tiny preview, or null on error
 */
export async function createLQIP(imageSrc: string): Promise<string | null> {
  try {
    // Load the full image
    const img = new Image();
    img.crossOrigin = 'anonymous';

    await new Promise<void>((resolve, reject) => {
      img.onload = () => resolve();
      img.onerror = () => reject(new Error('Failed to load image for LQIP'));
      img.src = imageSrc;
    });

    // Calculate aspect ratio preserving dimensions
    const aspect = img.naturalWidth / img.naturalHeight;
    const width = aspect >= 1 ? LQIP_SIZE : Math.round(LQIP_SIZE * aspect);
    const height = aspect >= 1 ? Math.round(LQIP_SIZE / aspect) : LQIP_SIZE;

    // Create canvas for downscaling
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    // Draw scaled down image
    ctx.drawImage(img, 0, 0, width, height);

    // Return as data URL (very small, ~1-2KB)
    return canvas.toDataURL('image/jpeg', LQIP_QUALITY);
  } catch {
    return null;
  }
}

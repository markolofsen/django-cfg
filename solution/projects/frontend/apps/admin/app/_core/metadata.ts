/**
 * Metadata Utilities
 *
 * Simple helper to automatically add OG images to page metadata
 * Uses app settings for configuration
 */

import type { Metadata } from 'next';
import { withOgImage } from '@djangocfg/nextjs/og-image';

/**
 * Generate metadata with automatic OG image
 *
 * Simple wrapper that automatically adds og:image using app settings
 *
 * @param metadata - Base metadata (title, description, etc.)
 *
 * @example
 * ```typescript
 * // In page.tsx
 * import { generateMetadata } from '@core/metadata';
 *
 * export const metadata = generateMetadata({
 *   title: 'My Page',
 *   description: 'Page description',
 * });
 * ```
 */
export function generateMetadata(metadata: Metadata): Metadata {
  return withOgImage(metadata, {
    preset: 'DARK_BLUE',
  });
}

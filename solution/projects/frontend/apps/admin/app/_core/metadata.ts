/**
 * Metadata Utilities
 *
 * Simple helper to automatically add OG images to page metadata
 * Uses app settings for configuration
 */

import type { Metadata } from 'next';
import { generateOgImageMetadata } from '@djangocfg/nextjs/og-image';
import { settings } from './settings';

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
  // Automatically add OG image (title and description will be auto-extracted from metadata)
  // Also automatically handles metadataBase if siteUrl is an absolute URL
  return generateOgImageMetadata(
    metadata,
    undefined, // Auto-extract from metadata
    {
      ogImageBaseUrl: 'https://djangocfg.com/api/og', // or '/api/og',
      siteUrl: settings.app.siteUrl, // Pass siteUrl for metadataBase auto-detection
      defaultParams: {
        siteName: settings.app.name,
        logo: settings.app.icons.logoVector,
      },
    }
  );
}


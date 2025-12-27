/**
 * Metadata Utilities
 *
 * Simple helper to automatically add OG images to page metadata
 * Uses app settings for configuration
 */

import type { Metadata } from 'next';
import { generateAppMetadata as generateAppMetadataBase } from '@djangocfg/nextjs/og-image';
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
  // Automatically add OG image, favicon, and apple icon
  // Also automatically handles metadataBase if siteUrl is an absolute URL
  return generateAppMetadataBase(
    metadata,
    undefined, // Auto-extract from metadata
    {
      // ogImageBaseUrl: 'https://djangocfg.com/api/og',
      siteUrl: settings.app.siteUrl,
      favicon: settings.app.media.favicon,
      appleIcon: settings.app.media.logo192,
      defaultParams: {
        siteName: settings.app.name,
        logo: settings.app.media.logoVector,
      },
    }
  );
}

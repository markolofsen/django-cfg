/**
 * PWA Manifest Metadata Utilities
 *
 * Helper functions for creating Next.js metadata for PWA manifest
 */

import type { Metadata, MetadataRoute, Viewport } from 'next';

export interface ManifestConfig {
  name: string;
  shortName?: string;
  description?: string;
  themeColor?: string;
  backgroundColor?: string;
  /** iOS status bar in the installed app. @default 'default' */
  statusBarStyle?: 'default' | 'black' | 'black-translucent';
  display?: 'standalone' | 'fullscreen' | 'minimal-ui' | 'browser';
  orientation?: 'portrait' | 'landscape' | 'any';
  startUrl?: string;
  scope?: string;
  lang?: string;
  dir?: 'ltr' | 'rtl' | 'auto';
  icons?: {
    src: string;
    sizes: string;
    type?: string;
    purpose?: string;
  }[];
}

/**
 * Icon paths configuration
 */
export interface IconPaths {
  logo192?: string;
  logo384?: string;
  logo512?: string;
}

/**
 * Protocol handler configuration
 * Allows your PWA to register as a handler for custom protocols
 *
 * @example
 * ```typescript
 * {
 *   protocol: "web+music",
 *   url: "/play?track=%s"
 * }
 * ```
 */
export interface ProtocolHandler {
  /** Protocol scheme (e.g., "web+music", "mailto", "magnet") */
  protocol: string;
  /** URL template with %s placeholder for the protocol parameter */
  url: string;
}

/**
 * Create viewport configuration for Next.js app
 *
 * @example
 * ```typescript
 * export const viewport: Viewport = createViewport({
 *   themeColor: '#ffffff',
 * });
 * ```
 */
export function createViewport(config: {
  themeColor?: string;
  /** `'cover'` lets the page extend under the notch / status bar and makes `env(safe-area-inset-*)` non-zero (needed for PWAs). @default 'cover' */
  viewportFit?: 'auto' | 'contain' | 'cover';
  /**
   * Also adds `maximumScale: 1` and `userScalable: false`. OFF by default on purpose: it blocks pinch-zoom for
   * people who need it (WCAG 1.4.4) and iOS Safari ignores `user-scalable=no` anyway. Double-tap zoom is already
   * off through `touch-action: manipulation` in the ui-core base styles; prefer that.
   */
  appLike?: boolean;
}): Viewport {
  return {
    viewportFit: config.viewportFit ?? 'cover',
    ...(config.appLike ? { userScalable: false } : {}),
    width: 'device-width',
    initialScale: 1,
    ...(config.appLike ? { maximumScale: 1 } : {}),
    themeColor: config.themeColor || '#000000',
  };
}

/**
 * Create manifest metadata for Next.js app
 *
 * Note: themeColor and viewport should be exported separately using createViewport()
 *
 * @example
 * ```typescript
 * export const metadata: Metadata = {
 *   ...createManifestMetadata({
 *     name: 'My App',
 *     shortName: 'App',
 *     description: 'My awesome app',
 *   }),
 * };
 *
 * export const viewport: Viewport = createViewport({
 *   themeColor: '#ffffff',
 * });
 * ```
 */
export function createManifestMetadata(config: ManifestConfig): Metadata {
  return {
    manifest: '/manifest.json',
    appleWebApp: {
      capable: true,
      statusBarStyle: config.statusBarStyle ?? 'default',
      title: config.shortName || config.name,
    },
    applicationName: config.name,
    formatDetection: {
      telephone: false,
    },
  };
}

/**
 * Create Next.js manifest function
 *
 * Use this in your app/manifest.ts file
 *
 * @example
 * ```typescript
 * // app/manifest.ts
 * import { createManifest } from '@djangocfg/nextjs/config';
 * import { settings } from '@core/settings';
 *
 * export default createManifest({
 *   name: settings.app.name,
 *   description: settings.app.description,
 *   icons: {
 *     logo192: settings.app.icons.logo192,
 *     logo384: settings.app.icons.logo384,
 *     logo512: settings.app.icons.logo512,
 *   },
 * });
 * ```
 */
export interface ScreenshotConfig {
  src: string;
  sizes: string;
  type?: string;
  form_factor?: 'narrow' | 'wide';
  label?: string;
}

/**
 * Smart screenshot configuration
 * Automatically detects everything from path or uses defaults
 */
export interface SmartScreenshotInput {
  src: string;
  /** Form factor (auto-detected from filename if contains 'desktop'/'mobile', or use default) */
  form_factor?: 'narrow' | 'wide';
  /** Optional label (auto-generated from form_factor) */
  label?: string;
  /** Optional width (defaults based on form_factor) */
  width?: number;
  /** Optional height (defaults based on form_factor) */
  height?: number;
}

/**
 * Create screenshot config with smart defaults
 * Automatically detects type, sizes, form_factor from path or uses sensible defaults
 *
 * @example
 * ```typescript
 * // Minimal - everything auto-detected
 * createScreenshot({ src: '/screenshots/desktop-view.png' })
 * // → form_factor: 'wide', sizes: '1920x1080', type: 'image/png', label: 'Desktop screenshot'
 *
 * createScreenshot({ src: '/screenshots/mobile.png' })
 * // → form_factor: 'narrow', sizes: '390x844', type: 'image/png', label: 'Mobile screenshot'
 *
 * // With custom dimensions
 * createScreenshot({ src: '/screenshots/tablet.png', width: 1024, height: 768 })
 * ```
 */
export function createScreenshot(input: SmartScreenshotInput | string): ScreenshotConfig {
  // Allow string shorthand
  const config = typeof input === 'string' ? { src: input } : input;
  const { src, label, form_factor } = config;
  let { width, height } = config;

  // Auto-detect image type from extension
  const ext = src.split('.').pop()?.toLowerCase();
  const typeMap: Record<string, string> = {
    png: 'image/png',
    jpg: 'image/jpeg',
    jpeg: 'image/jpeg',
    webp: 'image/webp',
    svg: 'image/svg+xml',
  };
  const type = ext ? typeMap[ext] || 'image/png' : 'image/png';

  // Try to parse dimensions from filename (e.g., "1920x1080.png" or "screenshot-390x844.png")
  const filename = src.toLowerCase();
  // Destructured: `\d{3,4}` cannot match empty, so both groups exist whenever
  // the match does — but only binding them says so without an assertion.
  const [, matchedWidth, matchedHeight] = filename.match(/(\d{3,4})x(\d{3,4})/) ?? [];
  if (matchedWidth && matchedHeight && !width && !height) {
    width = parseInt(matchedWidth, 10);
    height = parseInt(matchedHeight, 10);
  }

  // Auto-detect form_factor from filename if not provided
  let autoFormFactor: 'narrow' | 'wide' = 'wide'; // Default to wide
  if (filename.includes('mobile') || filename.includes('phone') || filename.includes('narrow')) {
    autoFormFactor = 'narrow';
  } else if (filename.includes('desktop') || filename.includes('laptop') || filename.includes('wide')) {
    autoFormFactor = 'wide';
  } else if (width && height) {
    // Calculate from dimensions if provided or parsed
    const aspectRatio = width / height;
    autoFormFactor = aspectRatio > 1.2 ? 'wide' : 'narrow';
  }

  const finalFormFactor = form_factor || autoFormFactor;

  // Default dimensions based on form_factor (only if not parsed from filename)
  const defaultDimensions = finalFormFactor === 'wide'
    ? { width: 1920, height: 1080 } // Desktop default
    : { width: 390, height: 844 };  // Mobile default (iPhone 14)

  const finalWidth = width || defaultDimensions.width;
  const finalHeight = height || defaultDimensions.height;

  // Auto-generate label
  const autoLabel = finalFormFactor === 'wide'
    ? 'Desktop screenshot'
    : 'Mobile screenshot';

  return {
    src,
    sizes: `${finalWidth}x${finalHeight}`,
    type,
    form_factor: finalFormFactor,
    label: label || autoLabel,
  };
}

/**
 * Create multiple screenshots from array
 * Supports string shorthand or full config objects
 *
 * @example
 * ```typescript
 * // Minimal - just paths
 * createScreenshots([
 *   '/screenshots/desktop.png',  // Auto: wide, 1920x1080
 *   '/screenshots/mobile.png',   // Auto: narrow, 390x844
 * ])
 *
 * // Mixed
 * createScreenshots([
 *   '/screenshots/desktop.png',
 *   { src: '/screenshots/tablet.png', width: 1024, height: 768 },
 * ])
 * ```
 */
export function createScreenshots(inputs: Array<SmartScreenshotInput | string>): ScreenshotConfig[] {
  return inputs.map(createScreenshot);
}

export function createManifest(config: {
  name: string;
  shortName?: string;
  description?: string;
  themeColor?: string;
  backgroundColor?: string;
  display?: 'standalone' | 'fullscreen' | 'minimal-ui' | 'browser';
  orientation?: 'portrait' | 'landscape' | 'any';
  id?: string;
  startUrl?: string;
  scope?: string;
  lang?: string;
  dir?: 'ltr' | 'rtl' | 'auto';
  icons?: IconPaths | ManifestConfig['icons'];
  screenshots?: ScreenshotConfig[];
  protocol_handlers?: ProtocolHandler[];
}): () => MetadataRoute.Manifest {
  return () => {
    // Convert IconPaths to manifest icons format
    let manifestIcons: MetadataRoute.Manifest['icons'];

    if (Array.isArray(config.icons)) {
      // Already in manifest format
      manifestIcons = config.icons as MetadataRoute.Manifest['icons'];
    } else if (config.icons) {
      // Convert IconPaths to manifest icons
      const { logo192, logo384, logo512 } = config.icons as IconPaths;
      manifestIcons = [
        ...(logo192
          ? [
              {
                src: logo192,
                sizes: '192x192',
                type: 'image/png',
                purpose: 'maskable' as const,
              },
            ]
          : []),
        ...(logo384
          ? [
              {
                src: logo384,
                sizes: '384x384',
                type: 'image/png',
              },
            ]
          : []),
        ...(logo512
          ? [
              {
                src: logo512,
                sizes: '512x512',
                type: 'image/png',
              },
            ]
          : []),
      ];
    }

    const manifest: MetadataRoute.Manifest = {
      name: config.name,
      short_name: config.shortName || config.name,
      description: config.description || config.name,
      id: config.id || config.startUrl || '/',
      start_url: config.startUrl || '/',
      scope: config.scope || '/',
      display: config.display || 'standalone',
      orientation: config.orientation || 'portrait',
      background_color: config.backgroundColor || '#000000',
      theme_color: config.themeColor || '#ffffff',
      lang: config.lang || 'en',
      dir: config.dir || 'ltr',
      icons: manifestIcons,
      // Removed forced gcm_sender_id to avoid potential conflicts with VAPID
      // gcm_sender_id: '103953800507',
    };

    // Add screenshots if provided (for Richer PWA Install UI)
    if (config.screenshots && config.screenshots.length > 0) {
      manifest.screenshots = config.screenshots;
    }

    // Add protocol handlers if provided
    if (config.protocol_handlers && config.protocol_handlers.length > 0) {
      manifest.protocol_handlers = config.protocol_handlers;
    }

    return manifest;
  };
}

/**
 * Generate manifest.json content (legacy)
 *
 * @deprecated Use createManifest() instead
 */
export function generateManifest(config: ManifestConfig): MetadataRoute.Manifest {
  return createManifest(config)();
}

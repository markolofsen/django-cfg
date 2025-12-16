/**
 * Django CFG Admin Settings
 * 
 * Centralized configuration for the admin application.
 * Handles both development and static build modes.
 */

// ============================================================================
// Environment Detection
// ============================================================================

export const isDevelopment = process.env.NODE_ENV === 'development';
export const isProduction = !isDevelopment;
export const isStaticBuild = process.env.NEXT_PUBLIC_STATIC_BUILD === 'true';

// ============================================================================
// Environment Variables
// ============================================================================

/**
 * Base path for static builds (used when serving from Django).
 * Example: '/cfg/admin'
 */
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';

/**
 * Site URL for metadataBase auto-detection.
 * Used for generating absolute URLs in metadata (OG images, etc.).
 */
const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || '';

/**
 * API URL: empty string for static builds (relative paths), or localhost for dev.
 * Empty string allows using relative paths in static builds.
 */
const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Generates static asset path based on build mode.
 * 
 * @param path - Relative path from static directory (e.g., 'logos/vector.svg')
 * @returns Absolute or relative path depending on build mode
 */
const getStaticAssetPath = (path: string): string => {
  const staticBase = isStaticBuild ? basePath : siteUrl;
  return `${staticBase}/static/${path}`;
};

// ============================================================================
// Application Settings
// ============================================================================

export const settings = {
  // Application metadata
  app: {
    name: 'Django CFG',
    version: '1.0.0',
    description: 'Django CFG Admin Panel',
    siteUrl,
    icons: {
      logo192: getStaticAssetPath('logos/192x192.png'),
      logo384: getStaticAssetPath('logos/384x384.png'),
      logo512: getStaticAssetPath('logos/512x512.png'),
      logoVector: getStaticAssetPath('logos/vector.svg'),
    },
  },

  // Build configuration
  basePath,
  isStaticBuild,

  // API configuration
  api: {
    /**
     * Main API URL for authentication and CFG services.
     * 
     * For static builds: empty string (uses relative paths).
     * For development: typically 'http://localhost:8000'.
     * 
     * Note: Using || instead of ?? to allow empty string fallback.
     */
    baseUrl: apiUrl,
  },

  // Analytics configuration
  analytics: {
    googleTrackingId: 'G-3TWHNNC02S',
  },

  // Contact information
  contact: {
    email: 'info@djangocfg.com',
  },

  // Layout configuration
  layouts: {
    showChat: false,
    enablePhoneAuth: false,
  },

  // Links configuration
  links: {
    docsUrl: 'https://djangocfg.com',
  },

  // Push notifications configuration
  push: {
    vapidPublicKey: process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY || '',
  },
} as const;

// ============================================================================
// Type Exports
// ============================================================================

export type Settings = typeof settings;

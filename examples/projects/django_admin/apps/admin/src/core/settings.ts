/**
 * Unrealon Admin Settings
 */

export const isDevelopment = process.env.NODE_ENV === 'development';
export const isProduction = !isDevelopment;
export const isStaticBuild = process.env.NEXT_PUBLIC_STATIC_BUILD === 'true';

// Base path - comes from next.config.ts
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';
// API URL: empty string for static builds (relative paths), or localhost for dev
const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';

export const settings = {
  app: {
    name: 'Django CFG',
    version: '1.0.0',
    description: 'Django CFG Admin Panel',
    siteUrl: `${basePath}/`,
    icons: {
      logo192: `${basePath}/static/logos/192x192.png`,
      logo384: `${basePath}/static/logos/384x384.png`,
      logo512: `${basePath}/static/logos/512x512.png`,
      logoVector: `${basePath}/static/logos/vector.svg`,
    }
  },

  contact: {
    email: 'support@djangocfg.com',
  },

  layouts: {
    showChat: false,
    enablePhoneAuth: false,
  },

  api: {
    // Main API URL for authentication and CFG services
    // For static builds, NEXT_PUBLIC_API_URL is '' (empty string) to use relative paths
    // Use nullish coalescing (??) instead of || to allow empty string
    baseUrl: apiUrl,
    // WebSocket RPC URL (Django Channels)
    wsUrl: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8765',
    // Centrifugo WebSocket URL (NOTE: now received from API via connection-token endpoint)
    // centrifugoWsUrl: DEPRECATED - use tokenResponse.centrifugo_url from API
  },

  // Base path for static builds (used when serving from Django)
  basePath,

  // Build mode flag
  isStaticBuild,

  features: {
    search: false,
    notifications: false,
    darkMode: true,
  },

  swr: {
    refreshInterval: 0, // Disabled - using WebSocket for real-time updates
    revalidateOnFocus: false, // Disabled - using WebSocket for real-time updates
    revalidateOnReconnect: false, // Disabled - using WebSocket for real-time updates
  },

  admin: {
    url: `https://api.djangocfg.com/admin/`,
    demo: {
      email: 'admin@example.com',
      password: 'admin123',
    },
  },

  links: {
    docsUrl: 'https://djangocfg.com',
    githubUrl: 'https://github.com/markolofsen/django-cfg',
  },
} as const;

export type Settings = typeof settings;

/**
 * Unrealon Admin Settings
 */

export const isDevelopment = process.env.NODE_ENV === 'development';
export const isProduction = !isDevelopment;

export const settings = {
  app: {
    name: 'CFG Demo',
    version: '1.0.0',
    description: 'Django-CFG Demo',
    siteUrl: process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000',
    icons: {
      logo192: '/static/logos/192x192.png',
      logo384: '/static/logos/384x384.png',
      logo512: '/static/logos/512x512.png',
      logoVector: '/static/logos/vector.svg',
    }
  },

  contact: {
    email: 'support@djangocfg.com',
  },

  links: {
    documentationUrl: 'https://djangocfg.com',
  },

  layouts: {
    showChat: true,
    enablePhoneAuth: false,
  },

  api: {
    // Main API URL for authentication and CFG services
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    // WebSocket RPC URL (for IPC communication)
    wsUrl: process.env.NEXT_PUBLIC_WS_RPC_URL || 'ws://localhost:8965',

    // Router service (if needed)
    router: {
      baseUrl: process.env.NEXT_PUBLIC_ROUTER_API_URL || 'http://localhost:8083',
      wsUrl: process.env.NEXT_PUBLIC_ROUTER_WS_URL || 'ws://localhost:8083',
    },
    // Swarm service (if needed)
    swarm: {
      baseUrl: process.env.NEXT_PUBLIC_SWARM_API_URL || 'http://localhost:8010',
    },
  },

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
} as const;

export type Settings = typeof settings;

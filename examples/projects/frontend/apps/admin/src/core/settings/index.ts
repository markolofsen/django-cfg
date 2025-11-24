/**
 * App Settings
 */

export const settings = {
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || '',
  },
} as const;

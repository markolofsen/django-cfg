/**
 * Environment constants — shared across all @djangocfg packages.
 */

export const nodeEnv = process.env.NODE_ENV || 'development';
export const isDev = nodeEnv === 'development';
export const isProd = !isDev;
export const isTest = nodeEnv === 'test';
export const isBrowser = typeof window !== 'undefined';
export const isServer = typeof window === 'undefined';

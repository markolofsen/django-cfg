/**
 * Pure environment constants — shared across all @djangocfg UI packages.
 *
 * Keep this to framework-agnostic env primitives only. Feature flags that carry
 * domain meaning (e.g. static-build behaviour) live in the package that owns
 * them — `isStaticBuild` is exported from `@djangocfg/api` (the lowest shared
 * package).
 */

export const nodeEnv = process.env.NODE_ENV || 'development';
export const isDev = nodeEnv === 'development';
export const isProd = !isDev;
export const isTest = nodeEnv === 'test';
export const isBrowser = typeof window !== 'undefined';
export const isServer = typeof window === 'undefined';

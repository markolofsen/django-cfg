/**
 * Frontend configuration from environment variables
 */
import { isDev, isProd } from '@djangocfg/ui-core/lib';

export const config = {
  /**
   * Frontend build mode only; the server owns authentication policy.
   */
  isDevelopment: isDev,
  isProduction: isProd,
} as const;

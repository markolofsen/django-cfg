/**
 * RPC Logger Hook
 *
 * React hook for RPC logging using consola library.
 */

'use client';

import { useMemo } from 'react';
import { createConsola, type ConsolaInstance } from 'consola';
import { isDevelopment } from '@/core/settings';

export interface RPCLogger {
  info: (message: string) => void;
  debug: (message: string) => void;
  warning: (message: string) => void;
  error: (message: string, error?: Error) => void;
  success: (message: string) => void;
}

/**
 * React hook for RPC logger with consola
 *
 * @returns RPC logger instance
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const logger = useRPCLogger();
 *   logger.info('Connected to RPC server');
 * }
 * ```
 */
export function useRPCLogger(): RPCLogger {
  const logger = useMemo(() => {
    const consola = createConsola({
      level: isDevelopment ? 4 : 3, // debug in dev, info in prod
      formatOptions: {
        colors: true,
        date: false,
        compact: !isDevelopment,
      },
    }).withTag('RPC');

    return {
      info: (message: string) => {
        if (isDevelopment) consola.info(message);
      },
      debug: (message: string) => {
        if (isDevelopment) consola.debug(message);
      },
      warning: (message: string) => {
        if (isDevelopment) consola.warn(message);
      },
      error: (message: string, error?: Error) => {
        consola.error(message, error || '');
      },
      success: (message: string) => {
        if (isDevelopment) consola.success(message);
      },
    };
  }, []);

  return logger;
}

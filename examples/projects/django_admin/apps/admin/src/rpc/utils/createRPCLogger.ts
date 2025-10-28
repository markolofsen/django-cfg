/**
 * RPC Logger Utility
 *
 * Simple console-based logger for RPC communication.
 */

import { isDevelopment } from '@/core/settings';

export interface SimpleLogger {
  info: (message: string) => void;
  debug: (message: string) => void;
  warning: (message: string) => void;
  error: (message: string, error?: Error) => void;
  success: (message: string) => void;
}

/**
 * Create RPC logger with smart defaults
 *
 * @returns Simple logger instance
 */
export function createRPCLogger(): SimpleLogger {
  const shouldLog = isDevelopment;

  return {
    info: (message: string) => {
      if (shouldLog) console.info(`[RPC] ${message}`);
    },
    debug: (message: string) => {
      if (shouldLog) console.debug(`[RPC] ${message}`);
    },
    warning: (message: string) => {
      if (shouldLog) console.warn(`[RPC] ${message}`);
    },
    error: (message: string, error?: Error) => {
      console.error(`[RPC] ${message}`, error || '');
    },
    success: (message: string) => {
      if (shouldLog) console.log(`[RPC] ✅ ${message}`);
    },
  };
}

/**
 * Create a singleton RPC logger instance
 * Useful for sharing the same logger across multiple components
 */
let sharedLogger: SimpleLogger | null = null;

export function getSharedRPCLogger(): SimpleLogger {
  if (!sharedLogger) {
    sharedLogger = createRPCLogger();
  }
  return sharedLogger;
}

/**
 * Reset the shared logger instance
 * Useful for testing or when you need to recreate the logger
 */
export function resetSharedRPCLogger(): void {
  sharedLogger = null;
}

import { createConsola } from 'consola';

/**
 * Universal logger for @djangocfg/layouts
 * Uses consola for beautiful console logging
 * 
 * Log levels:
 * - 0: silent
 * - 1: fatal, error
 * - 2: warn
 * - 3: log, info
 * - 4: debug
 * - 5: trace, verbose
 */
export const logger = createConsola({
  level: process.env.NODE_ENV === 'production' ? 3 : 4,
}).withTag('layouts');

// ─────────────────────────────────────────────────────────────────────────
// Module-specific loggers
// ─────────────────────────────────────────────────────────────────────────

/**
 * Auth-specific logger
 */
export const authLogger = logger.withTag('auth');

/**
 * Chat-specific logger
 */
export const chatLogger = logger.withTag('chat');

/**
 * Support-specific logger
 */
export const supportLogger = logger.withTag('support');

/**
 * Payments-specific logger
 */
export const paymentsLogger = logger.withTag('payments');

/**
 * Profile-specific logger
 */
export const profileLogger = logger.withTag('profile');

/**
 * Dashboard-specific logger
 */
export const dashboardLogger = logger.withTag('dashboard');

// ─────────────────────────────────────────────────────────────────────────
// Export default
// ─────────────────────────────────────────────────────────────────────────

export default logger;

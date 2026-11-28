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
 *
 * Level is driven by the global runtime controller in @djangocfg/api so admins
 * get verbose logs (even in prod) and regular users keep a clean console.
 */
import { getLogLevel, onLogLevelChange } from '@djangocfg/api';

export const logger = createConsola({
  level: getLogLevel(),
}).withTag('layouts');

onLogLevelChange((level) => {
  logger.level = level;
});

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

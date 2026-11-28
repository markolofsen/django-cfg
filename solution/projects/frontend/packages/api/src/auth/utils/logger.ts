import { createConsola } from 'consola';

/**
 * Universal logger for @djangocfg/api/auth
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
 * The level is driven by the GLOBAL runtime controller (log-control), so an
 * admin can get verbose logs (even in prod) while regular users keep a clean
 * console. `applyRoleLogPolicy(...)` at app bootstrap sets the policy.
 */
import { getLogLevel, onLogLevelChange } from '../../log-control';

export const logger = createConsola({
  level: getLogLevel(),
}).withTag('api');

// Keep the live logger's level in sync with the global controller.
onLogLevelChange((level) => {
  logger.level = level;
});

/**
 * Auth-specific logger
 */
export const authLogger = logger.withTag('auth');

export default logger;

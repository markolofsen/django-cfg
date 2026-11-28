/**
 * Runtime Error Emitter
 *
 * Emits runtime errors as CustomEvents that can be caught by ErrorTrackingProvider.
 * This is a lightweight utility with no dependencies, suitable for use in any package.
 *
 * @example
 * ```ts
 * import { emitRuntimeError } from '@djangocfg/ui-core/utils';
 *
 * try {
 *   doSomething();
 * } catch (error) {
 *   emitRuntimeError('MyComponent', 'Failed to do something', error, { extra: 'context' });
 * }
 * ```
 */

/** Event name for runtime errors - must match ERROR_EVENTS.RUNTIME in layouts */
export const RUNTIME_ERROR_EVENT = 'runtime-error';

/**
 * Emit a runtime error event
 *
 * @param source - Error source identifier (e.g., 'Tour', 'Form', 'API')
 * @param message - Human-readable error message
 * @param error - Original Error object (optional)
 * @param context - Additional context data (optional)
 */
export function emitRuntimeError(
  source: string,
  message: string,
  error?: Error,
  context?: Record<string, unknown>
): void {
  if (typeof window === 'undefined') return;

  const event = new CustomEvent(RUNTIME_ERROR_EVENT, {
    detail: {
      source,
      message,
      error,
      context,
      timestamp: new Date(),
    },
  });

  window.dispatchEvent(event);
}

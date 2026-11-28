/**
 * useErrorEmitter - Universal error emitter hook
 *
 * Emits runtime errors that are caught by ErrorTrackingProvider
 * and displayed as toasts.
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { emitError } = useErrorEmitter('tour');
 *
 *   useEffect(() => {
 *     try {
 *       document.querySelectorAll(invalidSelector);
 *     } catch (error) {
 *       emitError('Invalid selector', error);
 *     }
 *   }, []);
 * }
 * ```
 */

'use client';

import { useCallback } from 'react';

import { ERROR_EVENTS } from '../types';

export interface EmitErrorOptions {
  /** Additional context data */
  context?: Record<string, unknown>;
}

export interface ErrorEmitter {
  /**
   * Emit an error to be shown as a toast
   * @param message - Human-readable error message
   * @param error - Original Error object (optional)
   * @param options - Additional options
   */
  emitError: (message: string, error?: Error, options?: EmitErrorOptions) => void;
}

/**
 * Hook to emit runtime errors
 *
 * @param source - Error source identifier (e.g., 'tour', 'form', 'api')
 */
export function useErrorEmitter(source: string): ErrorEmitter {
  const emitError = useCallback(
    (message: string, error?: Error, options?: EmitErrorOptions) => {
      if (typeof window === 'undefined') return;

      const event = new CustomEvent(ERROR_EVENTS.RUNTIME, {
        detail: {
          source,
          message,
          error,
          context: options?.context,
          timestamp: new Date(),
        },
      });

      window.dispatchEvent(event);
    },
    [source]
  );

  return { emitError };
}

export default useErrorEmitter;

/**
 * Error Tracking Hooks
 *
 * React hooks for accessing error state
 */

export { useErrors } from './providers/ErrorTrackingProvider';
export { useErrorEmitter } from './hooks/useErrorEmitter';
export type { ErrorEmitter, EmitErrorOptions } from './hooks/useErrorEmitter';

// Type exports for convenience
export type { ErrorTrackingContextValue } from './types';

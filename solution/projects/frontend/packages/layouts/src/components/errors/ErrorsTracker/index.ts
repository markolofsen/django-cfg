/**
 * Error Tracking - Unified error tracking for all error types
 *
 * Single provider and hook for validation, CORS, network, and runtime errors
 */

// Main provider and hook
export { ErrorTrackingProvider } from './providers/ErrorTrackingProvider';
export { useErrors } from './hooks';

// Error emitter hook (for emitting runtime errors from React components)
export { useErrorEmitter } from './hooks';
export type { ErrorEmitter, EmitErrorOptions } from './hooks';

// Re-export standalone emitRuntimeError from ui-core (for use outside React)
export { emitRuntimeError } from '@djangocfg/ui-core/utils';

// Types
export type {
  ErrorDetail,
  ValidationErrorDetail,
  CORSErrorDetail,
  NetworkErrorDetail,
  RuntimeErrorDetail,
  StoredError,
  ErrorTrackingConfig,
  ValidationErrorConfig,
  CORSErrorConfig,
  NetworkErrorConfig,
  RuntimeErrorConfig,
  ErrorTrackingContextValue,
  TrackedErrorType,
} from './types';

// Event names (for manual event dispatching)
export { ERROR_EVENTS } from './types';

// Components
export { ErrorButtons } from './components/ErrorButtons';
export { createErrorToast } from './components/ErrorToast';

// Utilities
export {
  formatZodIssues,
  formatValidationErrorForClipboard,
  formatCORSErrorForClipboard,
  formatNetworkErrorForClipboard,
  formatRuntimeErrorForClipboard,
  formatErrorTitle,
  extractDomain,
  errorDetailToDevtoolsEvent,
} from './utils/formatters';

export {
  generateCurl,
  generateCurlFromError,
  getAuthToken,
  type CurlOptions,
} from './utils/curl-generator';

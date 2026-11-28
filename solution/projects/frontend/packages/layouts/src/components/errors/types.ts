/**
 * Error Handling Configuration Types
 *
 * Configuration types for ErrorTrackingProvider and ErrorBoundary
 */

import type { ErrorInfo } from 'react';

// Re-export ErrorTrackingConfig from ErrorsTracker
export type {
  ErrorTrackingConfig,
  ValidationErrorConfig,
  CORSErrorConfig,
  NetworkErrorConfig,
  ErrorTypeConfig,
  ErrorDetail,
  ValidationErrorDetail,
  CORSErrorDetail,
  NetworkErrorDetail,
  StoredError,
  ErrorTrackingContextValue,
} from './ErrorsTracker/types';

/**
 * Error Boundary Configuration
 *
 * Configuration for React ErrorBoundary component
 */
export interface ErrorBoundaryConfig {
  /** Enable error boundary (default: true) */
  enabled?: boolean;

  /** Support email to display in error UI */
  supportEmail?: string;

  /** Custom error handler called when error is caught */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

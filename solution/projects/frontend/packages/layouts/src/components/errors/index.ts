/**
 * Error components exports
 */

export { ErrorBoundary } from './ErrorBoundary';
export { AppErrorFallback } from './AppErrorFallback';
export type { AppErrorFallbackProps } from './AppErrorFallback';
export { MonitorBoundary } from './MonitorBoundary';
export type { MonitorBoundaryProps } from './MonitorBoundary';
export { ErrorLayout } from './ErrorLayout';
export type { ErrorLayoutProps } from './ErrorLayout';
export { getErrorContent, ERROR_CODES } from './errorConfig';
export type { ErrorContent } from './errorConfig';

// Configuration types
export type {
  ErrorBoundaryConfig,
  ErrorTrackingConfig,
  ValidationErrorConfig,
  CORSErrorConfig,
  NetworkErrorConfig,
} from './types';


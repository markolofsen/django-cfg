/**
 * Error Tracking Types
 *
 * Common types for all error tracking functionality
 */

import type { ZodError } from 'zod';

/**
 * Base error detail from CustomEvent
 */
export interface BaseErrorDetail {
  /** Timestamp of the error */
  timestamp: Date;
  /** Support reference issued by the runtime (legacy events may omit it). */
  reference?: string;
}

/**
 * Validation error detail (from zod-validation-error event)
 */
export interface ValidationErrorDetail extends BaseErrorDetail {
  type: 'validation';
  /** Operation/function name that failed validation */
  operation: string;
  /** API endpoint path */
  path: string;
  /** HTTP method */
  method: string;
  /** Zod validation error */
  error: ZodError;
  /** Raw response data that failed validation */
  response: unknown;
}

/**
 * CORS error detail (from cors-error event)
 */
export interface CORSErrorDetail extends BaseErrorDetail {
  type: 'cors';
  /** API endpoint that was blocked */
  url: string;
  /** HTTP method */
  method: string;
  /** Error message */
  error: string;
}

/**
 * Network error detail (from network-error event)
 */
export interface NetworkErrorDetail extends BaseErrorDetail {
  type: 'network';
  /** API endpoint that failed */
  url: string;
  /** HTTP method */
  method: string;
  /** Error message */
  error: string;
  /** Status code if available */
  statusCode?: number;
  /**
   * Heuristic hint: request is cross-origin and PerformanceResourceTiming suggests
   * the connection reached the server but JS was blocked — likely a CORS policy issue.
   * Not definitive — browser intentionally prevents exact classification.
   */
  possibly_cors?: boolean;
}

/**
 * Every error category the tracker stores.
 *
 * Named rather than repeated inline: this union was written out twice — once
 * in `ErrorTrackingContextValue.clearErrorsByType` and once in the provider's
 * implementation of it — and the two drifted. `'runtime'` was added to the
 * interface but not to the implementation, so calling the documented API with
 * the documented argument failed to type-check, and consumers carried a patch
 * to paper over it. One definition means that cannot recur.
 */
export type TrackedErrorType =
  | 'validation'
  | 'cors'
  | 'network'
  | 'runtime';

/**
 * Runtime/generic error detail (from runtime-error event)
 * Used for any JS errors that need to be shown to user (e.g., Tour selector errors)
 */
export interface RuntimeErrorDetail extends BaseErrorDetail {
  type: 'runtime';
  /** Error source/category (e.g., 'tour', 'component', etc.) */
  source: string;
  /** Error message */
  message: string;
  /** Original error object if available */
  error?: Error;
  /** Additional context data */
  context?: Record<string, unknown>;
}

/**
 * Union type of all error details
 */
export type ErrorDetail = ValidationErrorDetail | CORSErrorDetail | NetworkErrorDetail | RuntimeErrorDetail;

/**
 * Stored error with unique ID
 */
export type StoredError<T extends ErrorDetail = ErrorDetail> = T & {
  /** Unique identifier for this error instance */
  id: string;
};

/**
 * Configuration for specific error type
 */
export interface ErrorTypeConfig {
  /**
   * Enable tracking for this error type
   * @default true
   */
  enabled?: boolean;

  /**
   * Show toast notifications
   * @default true
   */
  showToast?: boolean;

  /**
   * Maximum number of errors to keep in history
   * @default 50
   */
  maxErrors?: number;

  /**
   * Toast duration in milliseconds (0 = no auto-dismiss)
   * @default 8000 for validation, 0 for cors/network
   */
  duration?: number;
}

/**
 * Validation error specific config
 */
export interface ValidationErrorConfig extends ErrorTypeConfig {
  /**
   * Show operation name in toast
   * @default true
   */
  showOperation?: boolean;

  /**
   * Show endpoint path in toast
   * @default true
   */
  showPath?: boolean;

  /**
   * Show error count in toast
   * @default true
   */
  showErrorCount?: boolean;

  /**
   * Maximum number of issues to show in toast
   * @default 3
   */
  maxIssuesInToast?: number;
}

/**
 * CORS error specific config
 */
export interface CORSErrorConfig extends ErrorTypeConfig {
  /**
   * Show full URL in toast
   * @default true
   */
  showUrl?: boolean;

  /**
   * Show HTTP method in toast
   * @default true
   */
  showMethod?: boolean;
}

/**
 * Network error specific config
 */
export interface NetworkErrorConfig extends ErrorTypeConfig {
  /**
   * Show full URL in toast
   * @default true
   */
  showUrl?: boolean;

  /**
   * Show HTTP method in toast
   * @default true
   */
  showMethod?: boolean;

  /**
   * Show status code in toast
   * @default true
   */
  showStatusCode?: boolean;
}

/**
 * Runtime error specific config
 */
export interface RuntimeErrorConfig extends ErrorTypeConfig {
  /**
   * Show error source in toast
   * @default true
   */
  showSource?: boolean;
}

/**
 * Complete error tracking configuration
 */
export interface ErrorTrackingConfig {
  /**
   * Validation error tracking configuration
   */
  validation?: ValidationErrorConfig;

  /**
   * CORS error tracking configuration
   */
  cors?: CORSErrorConfig;

  /**
   * Network error tracking configuration
   */
  network?: NetworkErrorConfig;

  /**
   * Runtime error tracking configuration
   */
  runtime?: RuntimeErrorConfig;

  /**
   * Custom error handler (called before toast for all errors)
   * Return false to prevent default toast notification
   */
  onError?: (error: ErrorDetail) => boolean | void;
}

/**
 * Error tracking context value
 */
export interface ErrorTrackingContextValue {
  /** All errors */
  errors: StoredError[];

  /** Validation errors only */
  validationErrors: StoredError<ValidationErrorDetail>[];

  /** CORS errors only */
  corsErrors: StoredError<CORSErrorDetail>[];

  /** Network errors only */
  networkErrors: StoredError<NetworkErrorDetail>[];

  /** Runtime errors only */
  runtimeErrors: StoredError<RuntimeErrorDetail>[];

  /** Clear all errors */
  clearErrors: () => void;

  /** Clear errors by type */
  clearErrorsByType: (type: TrackedErrorType) => void;

  /** Clear specific error by ID */
  clearError: (id: string) => void;

  /** Get error count */
  errorCount: number;

  /** Get latest error */
  latestError: StoredError | null;

  /** Configuration */
  config: {
    validation: Required<ValidationErrorConfig>;
    cors: Required<CORSErrorConfig>;
    network: Required<NetworkErrorConfig>;
    runtime: Required<RuntimeErrorConfig>;
  };
}

/**
 * Event names for error tracking
 */
export const ERROR_EVENTS = {
  VALIDATION: 'zod-validation-error',
  CORS: 'cors-error',
  NETWORK: 'network-error',
  /** Runtime/generic errors (Tour, components, etc.) */
  RUNTIME: 'runtime-error',
} as const;

/**
 * Default configurations
 */
export const DEFAULT_ERROR_CONFIG: Required<ErrorTypeConfig> = {
  enabled: true,
  showToast: true,
  maxErrors: 50,
  duration: 8000,
};

export const DEFAULT_VALIDATION_CONFIG: Required<ValidationErrorConfig> = {
  ...DEFAULT_ERROR_CONFIG,
  showOperation: true,
  showPath: true,
  showErrorCount: true,
  maxIssuesInToast: 3,
};

export const DEFAULT_CORS_CONFIG: Required<CORSErrorConfig> = {
  ...DEFAULT_ERROR_CONFIG,
  duration: 0, // Don't auto-dismiss CORS errors
  showUrl: true,
  showMethod: true,
};

export const DEFAULT_NETWORK_CONFIG: Required<NetworkErrorConfig> = {
  ...DEFAULT_ERROR_CONFIG,
  duration: 0, // Don't auto-dismiss network errors
  showUrl: true,
  showMethod: true,
  showStatusCode: true,
};

export const DEFAULT_RUNTIME_CONFIG: Required<RuntimeErrorConfig> = {
  ...DEFAULT_ERROR_CONFIG,
  duration: 8000,
  showSource: true,
};

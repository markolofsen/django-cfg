/**
 * ErrorTrackingProvider - Universal error tracking
 *
 * Single provider that tracks all error types:
 * - Validation errors (Zod)
 * - CORS errors
 * - Network errors
 *
 * @example
 * ```tsx
 * // Default - all enabled
 * <ErrorTrackingProvider>
 *   <App />
 * </ErrorTrackingProvider>
 *
 * // Custom configuration
 * <ErrorTrackingProvider
 *   validation={{ showToast: true, maxErrors: 100 }}
 *   cors={{ enabled: true }}
 *   network={{ enabled: false }}
 * >
 *   <App />
 * </ErrorTrackingProvider>
 * ```
 */

'use client';

import React, {
    createContext, ReactNode, useCallback, useContext, useEffect, useMemo, useRef, useState
} from 'react';

import { toast } from '@djangocfg/ui-core/hooks';
import { useDebugMode, isProduction } from '@djangocfg/devtools';

import { generateErrorId, shouldShowError, shouldThrottleProdToast } from './errorDedupe';
import { createErrorToast } from '../components/ErrorToast';
import { generateShortErrorId, getProductionToast } from '../utils/formatters';
import {
    DEFAULT_CORS_CONFIG,
    DEFAULT_NETWORK_CONFIG,
    DEFAULT_RUNTIME_CONFIG,
    DEFAULT_VALIDATION_CONFIG,
    ERROR_EVENTS
} from '../types';

import type {
  ErrorDetail,
  StoredError,
  ValidationErrorConfig,
  CORSErrorConfig,
  NetworkErrorConfig,
  RuntimeErrorConfig,
  ValidationErrorDetail,
  CORSErrorDetail,
  NetworkErrorDetail,
  RuntimeErrorDetail,
  ErrorTrackingContextValue,
  TrackedErrorType,
} from '../types';
const ErrorTrackingContext = createContext<ErrorTrackingContextValue | undefined>(undefined);

export interface ErrorTrackingProviderProps {
  children: ReactNode;
  validation?: Partial<ValidationErrorConfig>;
  cors?: Partial<CORSErrorConfig>;
  network?: Partial<NetworkErrorConfig>;
  runtime?: Partial<RuntimeErrorConfig>;
  onError?: (error: ErrorDetail) => boolean | void;
  /** Called with the raw ErrorDetail for every tracked error. Wire to devtools.capture() (via errorDetailToDevtoolsEvent) to forward errors to the backend. */
  onMonitorCapture?: (detail: ErrorDetail) => void;
}

/**
 * Universal Error Tracking Provider
 *
 * Tracks all error types with a single provider
 */
export function ErrorTrackingProvider({
  children,
  validation: userValidationConfig,
  cors: userCorsConfig,
  network: userNetworkConfig,
  runtime: userRuntimeConfig,
  onError,
  onMonitorCapture,
}: ErrorTrackingProviderProps) {
  const [errors, setErrors] = useState<StoredError[]>([]);
  const isDebugMode = useDebugMode();

  // Merged configs must be referentially stable: they feed the listener effect
  // below, and a fresh object each render would detach and re-attach every
  // window listener on every render — including the re-render each tracked
  // error causes, dropping any error dispatched inside that gap.
  const validationConfig: Required<ValidationErrorConfig> = useMemo(
    () => ({ ...DEFAULT_VALIDATION_CONFIG, ...userValidationConfig }),
    [userValidationConfig]
  );

  const corsConfig: Required<CORSErrorConfig> = useMemo(
    () => ({ ...DEFAULT_CORS_CONFIG, ...userCorsConfig }),
    [userCorsConfig]
  );

  const networkConfig: Required<NetworkErrorConfig> = useMemo(
    () => ({ ...DEFAULT_NETWORK_CONFIG, ...userNetworkConfig }),
    [userNetworkConfig]
  );

  const runtimeConfig: Required<RuntimeErrorConfig> = useMemo(
    () => ({ ...DEFAULT_RUNTIME_CONFIG, ...userRuntimeConfig }),
    [userRuntimeConfig]
  );

  /**
   * Clear all errors
   */
  const clearErrors = useCallback(() => {
    setErrors([]);
  }, []);

  /**
   * Clear errors by type
   */
  const clearErrorsByType = useCallback((type: TrackedErrorType) => {
    setErrors((prev) => prev.filter((error) => error.type !== type));
  }, []);

  /**
   * Clear specific error
   */
  const clearError = useCallback((id: string) => {
    setErrors((prev) => prev.filter((error) => error.id !== id));
  }, []);

  /**
   * Handle any error event
   */
  const handleError = useCallback(
    (detail: ErrorDetail, config: Required<ValidationErrorConfig | CORSErrorConfig | NetworkErrorConfig | RuntimeErrorConfig>) => {
      // Check for duplicate errors (within deduplication window)
      const isUnique = shouldShowError(detail);

      // Create stored error with ID
      const storedError: StoredError = {
        ...detail,
        id: generateErrorId(detail.type),
      };

      // Add to errors array (limited by maxErrors)
      setErrors((prev) => {
        const updated = [storedError, ...prev];
        return updated.slice(0, config.maxErrors);
      });

      // Call custom error handler
      const shouldShowToast = onError?.(detail) !== false;

      // Forward raw ErrorDetail to monitor bridge only for unique errors
      // (prevents flooding ingest with duplicate events)
      if (onMonitorCapture && isUnique) {
        try {
          onMonitorCapture(detail);
        } catch { /* never crash */ }
      }

      // Show toast notification (only for unique errors)
      if (config.showToast && shouldShowToast && isUnique) {
        if (!isProduction || isDebugMode) {
          const toastOptions = createErrorToast(detail, config);
          toast.error(toastOptions.title, {
            description: toastOptions.description,
            duration: toastOptions.duration,
          });
        } else if (!shouldThrottleProdToast(detail.type)) {
          const errorId = detail.reference || generateShortErrorId();
          const { title, description } = getProductionToast(detail, errorId);
          toast.error(title, { description, duration: config.duration });
        }
      }
    },
    // `isProduction` is a module constant, not reactive state.
    [onError, onMonitorCapture, isDebugMode]
  );

  // The listener effect must not re-run when the handler changes identity: hosts
  // pass `onError`/`onMonitorCapture` as inline arrows, so `handleError` is new
  // on every render. Listeners read the current handler through this ref and
  // stay attached for the provider's whole lifetime.
  const handleErrorRef = useRef(handleError);
  useEffect(() => {
    handleErrorRef.current = handleError;
  }, [handleError]);

  /**
   * Setup event listeners
   */
  useEffect(() => {
    // Only run in browser
    if (typeof window === 'undefined') return;

    const handlers: Array<{ event: string; handler: (e: Event) => void }> = [];

    // Validation errors
    if (validationConfig.enabled) {
      const handler = (event: Event) => {
        if (!(event instanceof CustomEvent)) return;
        const raw = event.detail ?? {};
        // The generated client dispatches `{ operation, method, path, issues,
        // data, timestamp }` — i.e. `issues`/`data`, not a `ZodError` in
        // `error`. Normalise into the ValidationErrorDetail shape so the toast
        // can render issue count/messages (and never read undefined.issues).
        const error =
          raw.error && Array.isArray(raw.error.issues)
            ? raw.error
            : { issues: Array.isArray(raw.issues) ? raw.issues : [] };
        const detail: ValidationErrorDetail = {
          ...raw,
          type: 'validation' as const,
          error: error as ValidationErrorDetail['error'],
          response: raw.response ?? raw.data,
        };
        handleErrorRef.current(detail, validationConfig);
      };
      window.addEventListener(ERROR_EVENTS.VALIDATION, handler);
      handlers.push({ event: ERROR_EVENTS.VALIDATION, handler });
    }

    // Network errors (includes possibly_cors hint from generated clients)
    if (networkConfig.enabled) {
      const handler = (event: Event) => {
        if (!(event instanceof CustomEvent)) return;
        const detail: NetworkErrorDetail = {
          ...event.detail,
          type: 'network' as const,
        };
        handleErrorRef.current(detail, networkConfig);
      };
      window.addEventListener(ERROR_EVENTS.NETWORK, handler);
      handlers.push({ event: ERROR_EVENTS.NETWORK, handler });
    }

    // Runtime errors (generic JS errors from anywhere in the app)
    if (runtimeConfig.enabled) {
      const handler = (event: Event) => {
        if (!(event instanceof CustomEvent)) return;
        const detail: RuntimeErrorDetail = {
          type: 'runtime' as const,
          source: event.detail.source || 'unknown',
          message: event.detail.message || 'Unknown error',
          error: event.detail.error,
          context: event.detail.context,
          timestamp: event.detail.timestamp || new Date(),
        };
        handleErrorRef.current(detail, runtimeConfig);
      };
      window.addEventListener(ERROR_EVENTS.RUNTIME, handler);
      handlers.push({ event: ERROR_EVENTS.RUNTIME, handler });
    }

    // Cleanup
    return () => {
      handlers.forEach(({ event, handler }) => {
        window.removeEventListener(event, handler);
      });
    };
    // No `cors` listener: nothing dispatches `cors-error`. A blocked request
    // surfaces as a network error carrying `possibly_cors`, so `corsConfig`
    // configures presentation only and is not a dependency here.
  }, [validationConfig, networkConfig, runtimeConfig]);

  // Filter errors by type
  const validationErrors = errors.filter((e) => e.type === 'validation') as StoredError<ValidationErrorDetail>[];
  const corsErrors = errors.filter((e) => e.type === 'cors') as StoredError<CORSErrorDetail>[];
  const networkErrors = errors.filter((e) => e.type === 'network') as StoredError<NetworkErrorDetail>[];
  const runtimeErrors = errors.filter((e) => e.type === 'runtime') as StoredError<RuntimeErrorDetail>[];

  const value: ErrorTrackingContextValue = {
    errors,
    validationErrors,
    corsErrors,
    networkErrors,
    runtimeErrors,
    clearErrors,
    clearErrorsByType,
    clearError,
    errorCount: errors.length,
    latestError: errors[0] || null,
    config: {
      validation: validationConfig,
      cors: corsConfig,
      network: networkConfig,
      runtime: runtimeConfig,
    },
  };

  return (
    <ErrorTrackingContext.Provider value={value}>
      {children}
    </ErrorTrackingContext.Provider>
  );
}

/**
 * useErrors Hook
 *
 * Access errors from any component
 *
 * @example
 * ```tsx
 * function ErrorPanel() {
 *   const { errors, validationErrors, clearErrors } = useErrors();
 *
 *   return (
 *     <div>
 *       <h3>Errors ({errors.length})</h3>
 *       <h4>Validation: {validationErrors.length}</h4>
 *       <button onClick={clearErrors}>Clear All</button>
 *     </div>
 *   );
 * }
 * ```
 */
export function useErrors(): ErrorTrackingContextValue {
  const context = useContext(ErrorTrackingContext);

  if (context === undefined) {
    throw new Error('useErrors must be used within ErrorTrackingProvider');
  }

  return context;
}

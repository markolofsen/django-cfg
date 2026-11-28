/**
 * Error Formatters
 *
 * Format different error types for display and copying
 */

import type { ZodError } from 'zod';
import type { ValidationErrorDetail, CORSErrorDetail, NetworkErrorDetail, RuntimeErrorDetail, ErrorDetail } from '../types';
import type { DevtoolsEvent } from '@djangocfg/devtools';
import { EventType, EventLevel } from '@djangocfg/devtools';

/**
 * Safely read Zod issues. The error toast must never crash itself, so we
 * tolerate a missing/malformed `error` (e.g. a non-ZodError slipping through)
 * instead of throwing `Cannot read properties of undefined (reading 'issues')`.
 */
export function safeZodIssues(error: ZodError | null | undefined): ZodError['issues'] {
  const issues = (error as ZodError | undefined)?.issues;
  return Array.isArray(issues) ? issues : [];
}

/**
 * Format Zod error issues for display
 */
export function formatZodIssues(error: ZodError, maxIssues: number = 3): string {
  const allIssues = safeZodIssues(error);
  if (allIssues.length === 0) return '';

  const issues = allIssues.slice(0, maxIssues);
  const formatted = issues.map((issue) => {
    const path = issue.path.join('.') || 'root';
    return `${path}: ${issue.message}`;
  });

  if (allIssues.length > maxIssues) {
    formatted.push(`... and ${allIssues.length - maxIssues} more`);
  }

  return formatted.join(', ');
}

/**
 * Format validation error for clipboard
 */
export function formatValidationErrorForClipboard(detail: ValidationErrorDetail): string {
  const issues = safeZodIssues(detail.error);
  const errorData = {
    type: 'validation',
    timestamp: detail.timestamp.toISOString(),
    operation: detail.operation,
    endpoint: {
      method: detail.method,
      path: detail.path,
    },
    validation_errors: issues.map((issue) => ({
      path: issue.path.join('.') || 'root',
      message: issue.message,
      code: issue.code,
      ...(('expected' in issue) && { expected: issue.expected }),
      ...(('received' in issue) && { received: issue.received }),
      ...(('minimum' in issue) && { minimum: issue.minimum }),
      ...(('maximum' in issue) && { maximum: issue.maximum }),
    })),
    response: detail.response,
    total_errors: issues.length,
  };

  return JSON.stringify(errorData, null, 2);
}

/**
 * Format CORS error for clipboard
 */
export function formatCORSErrorForClipboard(detail: CORSErrorDetail): string {
  const errorData = {
    type: 'cors',
    timestamp: detail.timestamp.toISOString(),
    url: detail.url,
    method: detail.method,
    error: detail.error,
  };

  return JSON.stringify(errorData, null, 2);
}

/**
 * Format network error for clipboard
 */
export function formatNetworkErrorForClipboard(detail: NetworkErrorDetail): string {
  const errorData = {
    type: 'network',
    timestamp: detail.timestamp.toISOString(),
    url: detail.url,
    method: detail.method,
    error: detail.error,
    ...(detail.statusCode && { statusCode: detail.statusCode }),
  };

  return JSON.stringify(errorData, null, 2);
}

/**
 * Extract domain from URL
 */
export function extractDomain(url: string): string {
  try {
    const urlObj = new URL(url);
    return urlObj.origin;
  } catch {
    return url;
  }
}

/**
 * Format runtime error for clipboard
 */
export function formatRuntimeErrorForClipboard(detail: RuntimeErrorDetail): string {
  const errorData = {
    type: 'runtime',
    timestamp: detail.timestamp.toISOString(),
    source: detail.source,
    message: detail.message,
    ...(detail.error && {
      errorName: detail.error.name,
      errorMessage: detail.error.message,
      stack: detail.error.stack,
    }),
    ...(detail.context && { context: detail.context }),
  };

  return JSON.stringify(errorData, null, 2);
}

/**
 * Convert ErrorDetail to DevtoolsEvent for forwarding to the backend ingest.
 * Use via ErrorTrackingProvider.onMonitorCapture.
 */
export function errorDetailToDevtoolsEvent(detail: ErrorDetail): DevtoolsEvent {
  const url = typeof window !== 'undefined' ? window.location.href : ''
  switch (detail.type) {
    case 'validation':
      return { event_type: EventType.ERROR, level: EventLevel.WARNING, message: `Validation: ${detail.operation} ${detail.path}`, url }
    case 'cors':
      return { event_type: EventType.NETWORK_ERROR, level: EventLevel.ERROR, message: `CORS: ${detail.method} ${detail.url}`, http_method: detail.method, http_url: detail.url, url }
    case 'network':
      return { event_type: EventType.NETWORK_ERROR, level: detail.statusCode && detail.statusCode >= 500 ? EventLevel.ERROR : EventLevel.WARNING, message: `${detail.method} ${detail.url} → ${detail.statusCode ?? 'ERR'}`, http_method: detail.method, http_url: detail.url, http_status: detail.statusCode, url }
    case 'runtime':
      return { event_type: EventType.JS_ERROR, level: EventLevel.ERROR, message: detail.message, stack_trace: detail.error?.stack, url }
  }
}

/**
 * Format error title based on type (dev/debug mode — full details)
 */
export function formatErrorTitle(detail: ValidationErrorDetail | CORSErrorDetail | NetworkErrorDetail | RuntimeErrorDetail): string {
  switch (detail.type) {
    case 'validation':
      return `❌ Validation Error in ${detail.operation}`;
    case 'cors':
      return '⚠️ Server Unavailable';
    case 'network':
      return detail.statusCode
        ? `⚠️ Network Error (${detail.statusCode})`
        : '⚠️ Network Error';
    case 'runtime':
      return `⚠️ ${detail.source} Error`;
    default:
      return '❌ Error';
  }
}

/**
 * Generate short error ID for support reference
 * Format: ERR-XXXXX (base36, derived from timestamp + counter)
 */
let prodErrorCounter = 0;
export function generateShortErrorId(): string {
  const id = ((Date.now() % 1_000_000) + (++prodErrorCounter)).toString(36).toUpperCase().slice(-5);
  return `ERR-${id.padStart(5, '0')}`;
}

/**
 * Production-safe toast content — no internal details exposed
 * Returns user-friendly title + description with error ID for support
 */
export function getProductionToast(detail: ErrorDetail, errorId: string): { title: string; description: string } {
  switch (detail.type) {
    case 'validation':
      return {
        title: 'Invalid data received',
        description: `Please try again. Reference: ${errorId}`,
      };
    case 'cors':
      return {
        title: 'Server unavailable',
        description: `Unable to reach the server. Reference: ${errorId}`,
      };
    case 'network': {
      const status = detail.statusCode;
      if (status && status >= 200 && status < 300) {
        return {
          title: 'Invalid server response',
          description: `Please try again. Reference: ${errorId}`,
        };
      }
      if (status && status >= 500) {
        return {
          title: 'Server error',
          description: `We're working on it. Reference: ${errorId}`,
        };
      }
      if (status === 403) {
        return {
          title: 'Access denied',
          description: `You don't have permission. Reference: ${errorId}`,
        };
      }
      if (status === 404) {
        return {
          title: 'Not found',
          description: `The requested resource was not found. Reference: ${errorId}`,
        };
      }
      return {
        title: 'Connection error',
        description: `Please check your connection and try again. Reference: ${errorId}`,
      };
    }
    case 'runtime':
      return {
        title: 'Something went wrong',
        description: `An unexpected error occurred. Reference: ${errorId}`,
      };
    default:
      return {
        title: 'Something went wrong',
        description: `Please try again. Reference: ${errorId}`,
      };
  }
}

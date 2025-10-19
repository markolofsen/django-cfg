/**
 * Universal Error Configuration
 *
 * Provides standard error content for common HTTP status codes
 * Use this to maintain consistency across error pages
 */

import React from 'react';
import { FileQuestion, ServerCrash, ShieldAlert, Clock, AlertTriangle, Ban } from 'lucide-react';

export interface ErrorContent {
  title: string;
  description: string;
  icon: React.ReactNode;
}

/**
 * Get standardized error content based on status code
 *
 * @param statusCode - HTTP status code or custom error type
 * @returns Error content configuration
 *
 * @example
 * ```tsx
 * const { title, description, icon } = getErrorContent(404);
 * <ErrorLayout title={title} description={description} illustration={icon} />
 * ```
 */
export function getErrorContent(statusCode?: number | string): ErrorContent {
  const code = typeof statusCode === 'string' ? parseInt(statusCode, 10) : statusCode;

  switch (code) {
    // 400 Bad Request
    case 400:
      return {
        title: 'Bad Request',
        description: 'The request could not be understood. Please check your input and try again.',
        icon: <AlertTriangle className="w-24 h-24 text-warning/50" strokeWidth={1.5} />,
      };

    // 401 Unauthorized
    case 401:
      return {
        title: 'Authentication Required',
        description: 'You need to sign in to access this page.',
        icon: <ShieldAlert className="w-24 h-24 text-warning/50" strokeWidth={1.5} />,
      };

    // 403 Forbidden
    case 403:
      return {
        title: 'Access Denied',
        description: "You don't have permission to access this resource.",
        icon: <Ban className="w-24 h-24 text-destructive/50" strokeWidth={1.5} />,
      };

    // 404 Not Found
    case 404:
      return {
        title: 'Page Not Found',
        description: "The page you're looking for doesn't exist or has been moved.",
        icon: <FileQuestion className="w-24 h-24 text-muted-foreground/50" strokeWidth={1.5} />,
      };

    // 408 Request Timeout
    case 408:
      return {
        title: 'Request Timeout',
        description: 'The request took too long to process. Please try again.',
        icon: <Clock className="w-24 h-24 text-warning/50" strokeWidth={1.5} />,
      };

    // 500 Internal Server Error
    case 500:
      return {
        title: 'Server Error',
        description: "Something went wrong on our end. We're working to fix it.",
        icon: <ServerCrash className="w-24 h-24 text-destructive/50" strokeWidth={1.5} />,
      };

    // 502 Bad Gateway
    case 502:
      return {
        title: 'Bad Gateway',
        description: 'The server received an invalid response. Please try again later.',
        icon: <ServerCrash className="w-24 h-24 text-destructive/50" strokeWidth={1.5} />,
      };

    // 503 Service Unavailable
    case 503:
      return {
        title: 'Service Unavailable',
        description: 'The service is temporarily unavailable. Please try again later.',
        icon: <ServerCrash className="w-24 h-24 text-destructive/50" strokeWidth={1.5} />,
      };

    // 504 Gateway Timeout
    case 504:
      return {
        title: 'Gateway Timeout',
        description: 'The server took too long to respond. Please try again.',
        icon: <Clock className="w-24 h-24 text-warning/50" strokeWidth={1.5} />,
      };

    // Default / Unknown Error
    default:
      return {
        title: 'Something Went Wrong',
        description: 'An unexpected error occurred. Please try again or contact support.',
        icon: <AlertTriangle className="w-24 h-24 text-warning/50" strokeWidth={1.5} />,
      };
  }
}

/**
 * Common error codes as constants
 */
export const ERROR_CODES = {
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  TIMEOUT: 408,
  SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
} as const;

/**
 * Ready-to-use getInitialProps for Next.js _error.tsx page
 *
 * Extracts status code from response or error automatically
 * Works for both server-side and client-side errors
 *
 * @example
 * ```tsx
 * // pages/_error.tsx
 * import { ErrorLayout, errorPageGetInitialProps } from '@djangocfg/layouts';
 *
 * function ErrorPage({ statusCode }) {
 *   return <ErrorLayout code={statusCode} />;
 * }
 *
 * ErrorPage.getInitialProps = errorPageGetInitialProps;
 * export default ErrorPage;
 * ```
 */
export const errorPageGetInitialProps = ({ res, err }: any) => {
  const statusCode = res ? res.statusCode : err ? err.statusCode : 404;
  return { statusCode };
};

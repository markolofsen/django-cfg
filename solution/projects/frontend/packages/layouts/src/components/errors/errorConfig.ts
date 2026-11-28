/**
 * Universal Error Configuration
 *
 * Provides standard error content for common HTTP status codes
 * Use this to maintain consistency across error pages
 *
 * NOTE: Only returns primitives (title, description) - NO React components
 * This ensures safe serialization during prerendering
 */

export interface ErrorContent {
  title: string;
  description: string;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type TranslationFn = (key: any, params?: Record<string, string | number>) => string;

/**
 * Get standardized error content based on status code
 *
 * @param statusCode - HTTP status code or custom error type
 * @param t - Translation function from useT()
 * @returns Error content configuration (title and description only)
 *
 * @example
 * ```tsx
 * const { title, description } = getErrorContent(404, t);
 * <ErrorLayout title={title} description={description} code={404} />
 * ```
 */
export function getErrorContent(statusCode?: number | string, t?: TranslationFn): ErrorContent {
  const code = typeof statusCode === 'string' ? parseInt(statusCode, 10) : statusCode;

  // Helper to get translation or fallback
  const tr = (key: string, fallback: string) => t ? t(key) : fallback;

  switch (code) {
    // 400 Bad Request
    case 400:
      return {
        title: tr('layouts.errors.badRequest', 'Bad Request'),
        description: tr('layouts.errors.badRequestDesc', 'The request could not be understood. Please check your input and try again.'),
      };

    // 401 Unauthorized
    case 401:
      return {
        title: tr('layouts.errors.authRequired', 'Authentication Required'),
        description: tr('layouts.errors.authRequiredDesc', 'You need to sign in to access this page.'),
      };

    // 403 Forbidden
    case 403:
      return {
        title: tr('layouts.errors.accessDenied', 'Access Denied'),
        description: tr('layouts.errors.accessDeniedDesc', "You don't have permission to access this resource."),
      };

    // 404 Not Found
    case 404:
      return {
        title: tr('layouts.errors.pageNotFound', 'Page Not Found'),
        description: tr('layouts.errors.pageNotFoundDesc', "The page you're looking for doesn't exist or has been moved."),
      };

    // 408 Request Timeout
    case 408:
      return {
        title: tr('layouts.errors.requestTimeout', 'Request Timeout'),
        description: tr('layouts.errors.requestTimeoutDesc', 'The request took too long to process. Please try again.'),
      };

    // 500 Internal Server Error
    case 500:
      return {
        title: tr('layouts.errors.serverError', 'Server Error'),
        description: tr('layouts.errors.serverErrorDesc', "Something went wrong on our end. We're working to fix it."),
      };

    // 502 Bad Gateway
    case 502:
      return {
        title: tr('layouts.errors.badGateway', 'Bad Gateway'),
        description: tr('layouts.errors.badGatewayDesc', 'The server received an invalid response. Please try again later.'),
      };

    // 503 Service Unavailable
    case 503:
      return {
        title: tr('layouts.errors.serviceUnavailable', 'Service Unavailable'),
        description: tr('layouts.errors.serviceUnavailableDesc', 'The service is temporarily unavailable. Please try again later.'),
      };

    // 504 Gateway Timeout
    case 504:
      return {
        title: tr('layouts.errors.gatewayTimeout', 'Gateway Timeout'),
        description: tr('layouts.errors.gatewayTimeoutDesc', 'The server took too long to respond. Please try again.'),
      };

    // Default / Unknown Error
    default:
      return {
        title: tr('layouts.errors.somethingWentWrong', 'Something Went Wrong'),
        description: tr('layouts.errors.unknownErrorDesc', 'An unexpected error occurred. Please try again or contact support.'),
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


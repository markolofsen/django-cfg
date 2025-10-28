import { ProfilesProfiles } from "./profiles__api__profiles";
import { HttpClientAdapter, FetchAdapter } from "./http";
import { APIError, NetworkError } from "./errors";
import { APILogger, type LoggerConfig } from "./logger";
import { withRetry, type RetryConfig } from "./retry";


/**
 * Async API client for Django CFG API.
 *
 * Usage:
 * ```typescript
 * const client = new APIClient('https://api.example.com');
 * const users = await client.users.list();
 * const post = await client.posts.create(newPost);
 *
 * // Custom HTTP adapter (e.g., Axios)
 * const client = new APIClient('https://api.example.com', {
 *   httpClient: new AxiosAdapter()
 * });
 * ```
 */
export class APIClient {
  private baseUrl: string;
  private httpClient: HttpClientAdapter;
  private logger: APILogger | null = null;
  private retryConfig: RetryConfig | null = null;

  // Sub-clients
  public profiles_profiles: ProfilesProfiles;

  constructor(
    baseUrl: string,
    options?: {
      httpClient?: HttpClientAdapter;
      loggerConfig?: Partial<LoggerConfig>;
      retryConfig?: RetryConfig;
    }
  ) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.httpClient = options?.httpClient || new FetchAdapter();

    // Initialize logger if config provided
    if (options?.loggerConfig !== undefined) {
      this.logger = new APILogger(options.loggerConfig);
    }

    // Store retry configuration
    if (options?.retryConfig !== undefined) {
      this.retryConfig = options.retryConfig;
    }

    // Initialize sub-clients
    this.profiles_profiles = new ProfilesProfiles(this);
  }

  /**
   * Get CSRF token from cookies (for SessionAuthentication).
   *
   * Returns null if cookie doesn't exist (JWT-only auth).
   */
  getCsrfToken(): string | null {
    const name = 'csrftoken';
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
      return parts.pop()?.split(';').shift() || null;
    }
    return null;
  }

  /**
   * Make HTTP request with Django CSRF and session handling.
   * Automatically retries on network errors and 5xx server errors.
   */
  async request<T>(
    method: string,
    path: string,
    options?: {
      params?: Record<string, any>;
      body?: any;
      formData?: FormData;
      headers?: Record<string, string>;
    }
  ): Promise<T> {
    // Wrap request in retry logic if configured
    if (this.retryConfig) {
      return withRetry(() => this._makeRequest<T>(method, path, options), {
        ...this.retryConfig,
        onFailedAttempt: (info) => {
          // Log retry attempts
          if (this.logger) {
            this.logger.warn(
              `Retry attempt ${info.attemptNumber}/${info.retriesLeft + info.attemptNumber} ` +
              `for ${method} ${path}: ${info.error.message}`
            );
          }
          // Call user's onFailedAttempt if provided
          this.retryConfig?.onFailedAttempt?.(info);
        },
      });
    }

    // No retry configured, make request directly
    return this._makeRequest<T>(method, path, options);
  }

  /**
   * Internal request method (without retry wrapper).
   * Used by request() method with optional retry logic.
   */
  private async _makeRequest<T>(
    method: string,
    path: string,
    options?: {
      params?: Record<string, any>;
      body?: any;
      formData?: FormData;
      headers?: Record<string, string>;
    }
  ): Promise<T> {
    // Build URL - handle both absolute and relative paths
    // When baseUrl is empty (static builds), path is used as-is (relative to current origin)
    const url = this.baseUrl ? `${this.baseUrl}${path}` : path;
    const startTime = Date.now();

    // Build headers - start with custom headers from options
    const headers: Record<string, string> = {
      ...(options?.headers || {})
    };

    // Don't set Content-Type for FormData (browser will set it with boundary)
    if (!options?.formData && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    // CSRF not needed - SessionAuthentication not enabled in DRF config
    // Your API uses JWT/Token authentication (no CSRF required)

    // Log request
    if (this.logger) {
      this.logger.logRequest({
        method,
        url: url,
        headers,
        body: options?.formData || options?.body,
        timestamp: startTime,
      });
    }

    try {
      // Make request via HTTP adapter
      const response = await this.httpClient.request<T>({
        method,
        url: url,
        headers,
        params: options?.params,
        body: options?.body,
        formData: options?.formData,
      });

      const duration = Date.now() - startTime;

      // Check for HTTP errors
      if (response.status >= 400) {
        const error = new APIError(
          response.status,
          response.statusText,
          response.data,
          url
        );

        // Log error
        if (this.logger) {
          this.logger.logError(
            {
              method,
              url: url,
              headers,
              body: options?.formData || options?.body,
              timestamp: startTime,
            },
            {
              message: error.message,
              statusCode: response.status,
              duration,
              timestamp: Date.now(),
            }
          );
        }

        throw error;
      }

      // Log successful response
      if (this.logger) {
        this.logger.logResponse(
          {
            method,
            url: url,
            headers,
            body: options?.formData || options?.body,
            timestamp: startTime,
          },
          {
            status: response.status,
            statusText: response.statusText,
            data: response.data,
            duration,
            timestamp: Date.now(),
          }
        );
      }

      return response.data as T;
    } catch (error) {
      const duration = Date.now() - startTime;

      // Re-throw APIError as-is
      if (error instanceof APIError) {
        throw error;
      }

      // Wrap other errors as NetworkError
      const networkError = error instanceof Error
        ? new NetworkError(error.message, url, error)
        : new NetworkError('Unknown error', url);

      // Log network error
      if (this.logger) {
        this.logger.logError(
          {
            method,
            url: url,
            headers,
            body: options?.formData || options?.body,
            timestamp: startTime,
          },
          {
            message: networkError.message,
            duration,
            timestamp: Date.now(),
          }
        );
      }

      throw networkError;
    }
  }
}

import { CfgAuth } from "./cfg__accounts__auth";
import { CfgBulkEmail } from "./cfg__newsletter__bulk_email";
import { CfgCampaigns } from "./cfg__newsletter__campaigns";
import { CfgLeadSubmission } from "./cfg__leads__lead_submission";
import { CfgLogs } from "./cfg__newsletter__logs";
import { CfgNewsletters } from "./cfg__newsletter__newsletters";
import { CfgSubscriptions } from "./cfg__newsletter__subscriptions";
import { CfgTesting } from "./cfg__newsletter__testing";
import { CfgUserProfile } from "./cfg__accounts__user_profile";
import { CfgAccounts } from "./cfg__accounts";
import { CfgEndpoints } from "./cfg__endpoints";
import { CfgHealth } from "./cfg__health";
import { CfgKnowbase } from "./cfg__knowbase";
import { CfgLeads } from "./cfg__leads";
import { CfgNewsletter } from "./cfg__newsletter";
import { CfgPayments } from "./cfg__payments";
import { CfgSupport } from "./cfg__support";
import { CfgTasks } from "./cfg__tasks";
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
  public cfg_auth: CfgAuth;
  public cfg_bulk_email: CfgBulkEmail;
  public cfg_campaigns: CfgCampaigns;
  public cfg_lead_submission: CfgLeadSubmission;
  public cfg_logs: CfgLogs;
  public cfg_newsletters: CfgNewsletters;
  public cfg_subscriptions: CfgSubscriptions;
  public cfg_testing: CfgTesting;
  public cfg_user_profile: CfgUserProfile;
  public cfg_accounts: CfgAccounts;
  public cfg_endpoints: CfgEndpoints;
  public cfg_health: CfgHealth;
  public cfg_knowbase: CfgKnowbase;
  public cfg_leads: CfgLeads;
  public cfg_newsletter: CfgNewsletter;
  public cfg_payments: CfgPayments;
  public cfg_support: CfgSupport;
  public cfg_tasks: CfgTasks;

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
    this.cfg_auth = new CfgAuth(this);
    this.cfg_bulk_email = new CfgBulkEmail(this);
    this.cfg_campaigns = new CfgCampaigns(this);
    this.cfg_lead_submission = new CfgLeadSubmission(this);
    this.cfg_logs = new CfgLogs(this);
    this.cfg_newsletters = new CfgNewsletters(this);
    this.cfg_subscriptions = new CfgSubscriptions(this);
    this.cfg_testing = new CfgTesting(this);
    this.cfg_user_profile = new CfgUserProfile(this);
    this.cfg_accounts = new CfgAccounts(this);
    this.cfg_endpoints = new CfgEndpoints(this);
    this.cfg_health = new CfgHealth(this);
    this.cfg_knowbase = new CfgKnowbase(this);
    this.cfg_leads = new CfgLeads(this);
    this.cfg_newsletter = new CfgNewsletter(this);
    this.cfg_payments = new CfgPayments(this);
    this.cfg_support = new CfgSupport(this);
    this.cfg_tasks = new CfgTasks(this);
  }

  /**
   * Get CSRF token from cookies.
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
    const url = new URL(path, this.baseUrl);
    const startTime = Date.now();

    // Build headers - start with custom headers from options
    const headers: Record<string, string> = {
      ...(options?.headers || {})
    };

    // Don't set Content-Type for FormData (browser will set it with boundary)
    if (!options?.formData && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    // Add CSRF token for non-GET requests
    if (method !== 'GET') {
      const csrfToken = this.getCsrfToken();
      if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
      }
    }

    // Log request
    if (this.logger) {
      this.logger.logRequest({
        method,
        url: url.toString(),
        headers,
        body: options?.formData || options?.body,
        timestamp: startTime,
      });
    }

    try {
      // Make request via HTTP adapter
      const response = await this.httpClient.request<T>({
        method,
        url: url.toString(),
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
          url.toString()
        );

        // Log error
        if (this.logger) {
          this.logger.logError(
            {
              method,
              url: url.toString(),
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
            url: url.toString(),
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
        ? new NetworkError(error.message, url.toString(), error)
        : new NetworkError('Unknown error', url.toString());

      // Log network error
      if (this.logger) {
        this.logger.logError(
          {
            method,
            url: url.toString(),
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

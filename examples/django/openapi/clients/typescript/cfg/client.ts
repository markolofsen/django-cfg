import { CfgAuthAPI } from "./cfg__accounts__auth";
import { CfgBulkEmailAPI } from "./cfg__newsletter__bulk_email";
import { CfgCampaignsAPI } from "./cfg__newsletter__campaigns";
import { CfgLeadSubmissionAPI } from "./cfg__leads__lead_submission";
import { CfgLogsAPI } from "./cfg__newsletter__logs";
import { CfgNewslettersAPI } from "./cfg__newsletter__newsletters";
import { CfgSubscriptionsAPI } from "./cfg__newsletter__subscriptions";
import { CfgTestingAPI } from "./cfg__newsletter__testing";
import { CfgUserProfileAPI } from "./cfg__accounts__user_profile";
import { CfgWebhooksAPI } from "./cfg__payments__webhooks";
import { CfgAccountsAPI } from "./cfg__accounts";
import { CfgLeadsAPI } from "./cfg__leads";
import { CfgNewsletterAPI } from "./cfg__newsletter";
import { CfgSupportAPI } from "./cfg__support";
import { CfgPaymentsAPI } from "./cfg__payments";
import { CfgTasksAPI } from "./cfg__tasks";
import { HttpClientAdapter, FetchAdapter } from "./http";
import { APIError, NetworkError } from "./errors";
import { APILogger, type LoggerConfig } from "./logger";


/**
 * Async API client for Django CFG Sample API.
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

  // Sub-clients
  public cfg_auth: CfgAuthAPI;
  public cfg_bulk_email: CfgBulkEmailAPI;
  public cfg_campaigns: CfgCampaignsAPI;
  public cfg_lead_submission: CfgLeadSubmissionAPI;
  public cfg_logs: CfgLogsAPI;
  public cfg_newsletters: CfgNewslettersAPI;
  public cfg_subscriptions: CfgSubscriptionsAPI;
  public cfg_testing: CfgTestingAPI;
  public cfg_user_profile: CfgUserProfileAPI;
  public cfg_webhooks: CfgWebhooksAPI;
  public cfg_accounts: CfgAccountsAPI;
  public cfg_leads: CfgLeadsAPI;
  public cfg_newsletter: CfgNewsletterAPI;
  public cfg_support: CfgSupportAPI;
  public cfg_payments: CfgPaymentsAPI;
  public cfg_tasks: CfgTasksAPI;

  constructor(
    baseUrl: string,
    options?: {
      httpClient?: HttpClientAdapter;
      loggerConfig?: Partial<LoggerConfig>;
    }
  ) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.httpClient = options?.httpClient || new FetchAdapter();

    // Initialize logger if config provided
    if (options?.loggerConfig !== undefined) {
      this.logger = new APILogger(options.loggerConfig);
    }

    // Initialize sub-clients
    this.cfg_auth = new CfgAuthAPI(this);
    this.cfg_bulk_email = new CfgBulkEmailAPI(this);
    this.cfg_campaigns = new CfgCampaignsAPI(this);
    this.cfg_lead_submission = new CfgLeadSubmissionAPI(this);
    this.cfg_logs = new CfgLogsAPI(this);
    this.cfg_newsletters = new CfgNewslettersAPI(this);
    this.cfg_subscriptions = new CfgSubscriptionsAPI(this);
    this.cfg_testing = new CfgTestingAPI(this);
    this.cfg_user_profile = new CfgUserProfileAPI(this);
    this.cfg_webhooks = new CfgWebhooksAPI(this);
    this.cfg_accounts = new CfgAccountsAPI(this);
    this.cfg_leads = new CfgLeadsAPI(this);
    this.cfg_newsletter = new CfgNewsletterAPI(this);
    this.cfg_support = new CfgSupportAPI(this);
    this.cfg_payments = new CfgPaymentsAPI(this);
    this.cfg_tasks = new CfgTasksAPI(this);
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
   */
  async request<T>(
    method: string,
    path: string,
    options?: {
      params?: Record<string, any>;
      body?: any;
      formData?: FormData;
    }
  ): Promise<T> {
    const url = new URL(path, this.baseUrl);
    const startTime = Date.now();

    // Build headers
    const headers: Record<string, string> = {};

    // Don't set Content-Type for FormData (browser will set it with boundary)
    if (!options?.formData) {
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

import { CfgAuth } from "./cfg__accounts__auth";
import { CfgBulkEmail } from "./cfg__newsletter__bulk_email";
import { CfgCampaigns } from "./cfg__newsletter__campaigns";
import { CfgCentrifugoAdminApi } from "./cfg__centrifugo__centrifugo_admin_api";
import { CfgCentrifugoAuth } from "./cfg__centrifugo__centrifugo_auth";
import { CfgCentrifugoMonitoring } from "./cfg__centrifugo__centrifugo_monitoring";
import { CfgCentrifugoTesting } from "./cfg__centrifugo__centrifugo_testing";
import { CfgDashboardApiZones } from "./cfg__dashboard__dashboard_api_zones";
import { CfgDashboardActivity } from "./cfg__dashboard__dashboard_activity";
import { CfgDashboardCharts } from "./cfg__dashboard__dashboard_charts";
import { CfgDashboardCommands } from "./cfg__dashboard__dashboard_commands";
import { CfgDashboardConfig } from "./cfg__dashboard__dashboard_config";
import { CfgDashboardOverview } from "./cfg__dashboard__dashboard_overview";
import { CfgDashboardStatistics } from "./cfg__dashboard__dashboard_statistics";
import { CfgDashboardSystem } from "./cfg__dashboard__dashboard_system";
import { CfgLeadSubmission } from "./cfg__leads__lead_submission";
import { CfgLogs } from "./cfg__newsletter__logs";
import { CfgNewsletters } from "./cfg__newsletter__newsletters";
import { CfgRqJobs } from "./cfg__rq__rq_jobs";
import { CfgRqMonitoring } from "./cfg__rq__rq_monitoring";
import { CfgRqQueues } from "./cfg__rq__rq_queues";
import { CfgRqRegistries } from "./cfg__rq__rq_registries";
import { CfgRqSchedules } from "./cfg__rq__rq_schedules";
import { CfgRqTesting } from "./cfg__rq__rq_testing";
import { CfgRqWorkers } from "./cfg__rq__rq_workers";
import { CfgSubscriptions } from "./cfg__newsletter__subscriptions";
import { CfgTesting } from "./cfg__newsletter__testing";
import { CfgUserProfile } from "./cfg__accounts__user_profile";
import { CfgAccounts } from "./cfg__accounts";
import { CfgCentrifugo } from "./cfg__centrifugo";
import { CfgEndpoints } from "./cfg__endpoints";
import { CfgGrpcApiKeys } from "./cfg__grpc__grpc_api_keys";
import { CfgGrpcCharts } from "./cfg__grpc__grpc_charts";
import { CfgGrpcConfiguration } from "./cfg__grpc__grpc_configuration";
import { CfgGrpcMonitoring } from "./cfg__grpc__grpc_monitoring";
import { CfgGrpcProtoFiles } from "./cfg__grpc__grpc_proto_files";
import { CfgGrpcServices } from "./cfg__grpc__grpc_services";
import { CfgGrpcTesting } from "./cfg__grpc__grpc_testing";
import { CfgHealth } from "./cfg__health";
import { CfgKnowbase } from "./cfg__knowbase";
import { CfgLeads } from "./cfg__leads";
import { CfgNewsletter } from "./cfg__newsletter";
import { CfgPayments } from "./cfg__payments";
import { CfgSupport } from "./cfg__support";
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
  public cfg_centrifugo_admin_api: CfgCentrifugoAdminApi;
  public cfg_centrifugo_auth: CfgCentrifugoAuth;
  public cfg_centrifugo_monitoring: CfgCentrifugoMonitoring;
  public cfg_centrifugo_testing: CfgCentrifugoTesting;
  public cfg_dashboard_api_zones: CfgDashboardApiZones;
  public cfg_dashboard_activity: CfgDashboardActivity;
  public cfg_dashboard_charts: CfgDashboardCharts;
  public cfg_dashboard_commands: CfgDashboardCommands;
  public cfg_dashboard_config: CfgDashboardConfig;
  public cfg_dashboard_overview: CfgDashboardOverview;
  public cfg_dashboard_statistics: CfgDashboardStatistics;
  public cfg_dashboard_system: CfgDashboardSystem;
  public cfg_lead_submission: CfgLeadSubmission;
  public cfg_logs: CfgLogs;
  public cfg_newsletters: CfgNewsletters;
  public cfg_rq_jobs: CfgRqJobs;
  public cfg_rq_monitoring: CfgRqMonitoring;
  public cfg_rq_queues: CfgRqQueues;
  public cfg_rq_registries: CfgRqRegistries;
  public cfg_rq_schedules: CfgRqSchedules;
  public cfg_rq_testing: CfgRqTesting;
  public cfg_rq_workers: CfgRqWorkers;
  public cfg_subscriptions: CfgSubscriptions;
  public cfg_testing: CfgTesting;
  public cfg_user_profile: CfgUserProfile;
  public cfg_accounts: CfgAccounts;
  public cfg_centrifugo: CfgCentrifugo;
  public cfg_endpoints: CfgEndpoints;
  public cfg_grpc_api_keys: CfgGrpcApiKeys;
  public cfg_grpc_charts: CfgGrpcCharts;
  public cfg_grpc_configuration: CfgGrpcConfiguration;
  public cfg_grpc_monitoring: CfgGrpcMonitoring;
  public cfg_grpc_proto_files: CfgGrpcProtoFiles;
  public cfg_grpc_services: CfgGrpcServices;
  public cfg_grpc_testing: CfgGrpcTesting;
  public cfg_health: CfgHealth;
  public cfg_knowbase: CfgKnowbase;
  public cfg_leads: CfgLeads;
  public cfg_newsletter: CfgNewsletter;
  public cfg_payments: CfgPayments;
  public cfg_support: CfgSupport;

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
    this.cfg_centrifugo_admin_api = new CfgCentrifugoAdminApi(this);
    this.cfg_centrifugo_auth = new CfgCentrifugoAuth(this);
    this.cfg_centrifugo_monitoring = new CfgCentrifugoMonitoring(this);
    this.cfg_centrifugo_testing = new CfgCentrifugoTesting(this);
    this.cfg_dashboard_api_zones = new CfgDashboardApiZones(this);
    this.cfg_dashboard_activity = new CfgDashboardActivity(this);
    this.cfg_dashboard_charts = new CfgDashboardCharts(this);
    this.cfg_dashboard_commands = new CfgDashboardCommands(this);
    this.cfg_dashboard_config = new CfgDashboardConfig(this);
    this.cfg_dashboard_overview = new CfgDashboardOverview(this);
    this.cfg_dashboard_statistics = new CfgDashboardStatistics(this);
    this.cfg_dashboard_system = new CfgDashboardSystem(this);
    this.cfg_lead_submission = new CfgLeadSubmission(this);
    this.cfg_logs = new CfgLogs(this);
    this.cfg_newsletters = new CfgNewsletters(this);
    this.cfg_rq_jobs = new CfgRqJobs(this);
    this.cfg_rq_monitoring = new CfgRqMonitoring(this);
    this.cfg_rq_queues = new CfgRqQueues(this);
    this.cfg_rq_registries = new CfgRqRegistries(this);
    this.cfg_rq_schedules = new CfgRqSchedules(this);
    this.cfg_rq_testing = new CfgRqTesting(this);
    this.cfg_rq_workers = new CfgRqWorkers(this);
    this.cfg_subscriptions = new CfgSubscriptions(this);
    this.cfg_testing = new CfgTesting(this);
    this.cfg_user_profile = new CfgUserProfile(this);
    this.cfg_accounts = new CfgAccounts(this);
    this.cfg_centrifugo = new CfgCentrifugo(this);
    this.cfg_endpoints = new CfgEndpoints(this);
    this.cfg_grpc_api_keys = new CfgGrpcApiKeys(this);
    this.cfg_grpc_charts = new CfgGrpcCharts(this);
    this.cfg_grpc_configuration = new CfgGrpcConfiguration(this);
    this.cfg_grpc_monitoring = new CfgGrpcMonitoring(this);
    this.cfg_grpc_proto_files = new CfgGrpcProtoFiles(this);
    this.cfg_grpc_services = new CfgGrpcServices(this);
    this.cfg_grpc_testing = new CfgGrpcTesting(this);
    this.cfg_health = new CfgHealth(this);
    this.cfg_knowbase = new CfgKnowbase(this);
    this.cfg_leads = new CfgLeads(this);
    this.cfg_newsletter = new CfgNewsletter(this);
    this.cfg_payments = new CfgPayments(this);
    this.cfg_support = new CfgSupport(this);
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

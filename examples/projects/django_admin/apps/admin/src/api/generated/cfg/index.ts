/**
 * Django CFG API - API Client with JWT Management
 *
 * Usage:
 * ```typescript
 * import { API } from './api';
 *
 * const api = new API('https://api.example.com');
 *
 * // Set JWT token
 * api.setToken('your-jwt-token', 'refresh-token');
 *
 * // Use API
 * const posts = await api.posts.list();
 * const user = await api.users.retrieve(1);
 *
 * // Check authentication
 * if (api.isAuthenticated()) {
 *   // ...
 * }
 *
 * // Custom storage with logging (for Electron/Node.js)
 * import { MemoryStorageAdapter, APILogger } from './storage';
 * const logger = new APILogger({ enabled: true, logLevel: 'debug' });
 * const api = new API('https://api.example.com', {
 *   storage: new MemoryStorageAdapter(logger),
 *   loggerConfig: { enabled: true, logLevel: 'debug' }
 * });
 *
 * // Get OpenAPI schema
 * const schema = api.getSchema();
 * ```
 */

import { APIClient } from "./client";
import { OPENAPI_SCHEMA } from "./schema";
import {
  StorageAdapter,
  LocalStorageAdapter,
  CookieStorageAdapter,
  MemoryStorageAdapter
} from "./storage";
import type { RetryConfig } from "./retry";
import type { LoggerConfig } from "./logger";
import { APILogger } from "./logger";
import { CfgAuth } from "./cfg__accounts__auth/client";
import { CfgBulkEmail } from "./cfg__newsletter__bulk_email/client";
import { CfgCampaigns } from "./cfg__newsletter__campaigns/client";
import { CfgCentrifugoAdminApi } from "./cfg__centrifugo__centrifugo_admin_api/client";
import { CfgCentrifugoMonitoring } from "./cfg__centrifugo__centrifugo_monitoring/client";
import { CfgCentrifugoTesting } from "./cfg__centrifugo__centrifugo_testing/client";
import { CfgDashboardApiZones } from "./cfg__dashboard__dashboard_api_zones/client";
import { CfgDashboardActivity } from "./cfg__dashboard__dashboard_activity/client";
import { CfgDashboardCharts } from "./cfg__dashboard__dashboard_charts/client";
import { CfgDashboardCommands } from "./cfg__dashboard__dashboard_commands/client";
import { CfgDashboardOverview } from "./cfg__dashboard__dashboard_overview/client";
import { CfgDashboardStatistics } from "./cfg__dashboard__dashboard_statistics/client";
import { CfgDashboardSystem } from "./cfg__dashboard__dashboard_system/client";
import { CfgLeadSubmission } from "./cfg__leads__lead_submission/client";
import { CfgLogs } from "./cfg__newsletter__logs/client";
import { CfgNewsletters } from "./cfg__newsletter__newsletters/client";
import { CfgRqJobs } from "./cfg__rq__rq_jobs/client";
import { CfgRqMonitoring } from "./cfg__rq__rq_monitoring/client";
import { CfgRqQueues } from "./cfg__rq__rq_queues/client";
import { CfgRqRegistries } from "./cfg__rq__rq_registries/client";
import { CfgRqSchedules } from "./cfg__rq__rq_schedules/client";
import { CfgRqTesting } from "./cfg__rq__rq_testing/client";
import { CfgRqWorkers } from "./cfg__rq__rq_workers/client";
import { CfgSubscriptions } from "./cfg__newsletter__subscriptions/client";
import { CfgTesting } from "./cfg__newsletter__testing/client";
import { CfgUserProfile } from "./cfg__accounts__user_profile/client";
import { CfgAccounts } from "./cfg__accounts/client";
import { CfgCentrifugo } from "./cfg__centrifugo/client";
import { CfgEndpoints } from "./cfg__endpoints/client";
import { CfgGrpcMonitoring } from "./cfg__grpc__grpc_monitoring/client";
import { CfgHealth } from "./cfg__health/client";
import { CfgKnowbase } from "./cfg__knowbase/client";
import { CfgLeads } from "./cfg__leads/client";
import { CfgNewsletter } from "./cfg__newsletter/client";
import { CfgPayments } from "./cfg__payments/client";
import { CfgSupport } from "./cfg__support/client";
export * as CfgAuthTypes from "./cfg__accounts__auth/models";
export * as CfgBulkEmailTypes from "./cfg__newsletter__bulk_email/models";
export * as CfgCampaignsTypes from "./cfg__newsletter__campaigns/models";
export * as CfgCentrifugoAdminApiTypes from "./cfg__centrifugo__centrifugo_admin_api/models";
export * as CfgCentrifugoMonitoringTypes from "./cfg__centrifugo__centrifugo_monitoring/models";
export * as CfgCentrifugoTestingTypes from "./cfg__centrifugo__centrifugo_testing/models";
export * as CfgDashboardApiZonesTypes from "./cfg__dashboard__dashboard_api_zones/models";
export * as CfgDashboardActivityTypes from "./cfg__dashboard__dashboard_activity/models";
export * as CfgDashboardChartsTypes from "./cfg__dashboard__dashboard_charts/models";
export * as CfgDashboardCommandsTypes from "./cfg__dashboard__dashboard_commands/models";
export * as CfgDashboardOverviewTypes from "./cfg__dashboard__dashboard_overview/models";
export * as CfgDashboardStatisticsTypes from "./cfg__dashboard__dashboard_statistics/models";
export * as CfgDashboardSystemTypes from "./cfg__dashboard__dashboard_system/models";
export * as CfgLeadSubmissionTypes from "./cfg__leads__lead_submission/models";
export * as CfgLogsTypes from "./cfg__newsletter__logs/models";
export * as CfgNewslettersTypes from "./cfg__newsletter__newsletters/models";
export * as CfgRqJobsTypes from "./cfg__rq__rq_jobs/models";
export * as CfgRqMonitoringTypes from "./cfg__rq__rq_monitoring/models";
export * as CfgRqQueuesTypes from "./cfg__rq__rq_queues/models";
export * as CfgRqRegistriesTypes from "./cfg__rq__rq_registries/models";
export * as CfgRqSchedulesTypes from "./cfg__rq__rq_schedules/models";
export * as CfgRqTestingTypes from "./cfg__rq__rq_testing/models";
export * as CfgRqWorkersTypes from "./cfg__rq__rq_workers/models";
export * as CfgSubscriptionsTypes from "./cfg__newsletter__subscriptions/models";
export * as CfgTestingTypes from "./cfg__newsletter__testing/models";
export * as CfgUserProfileTypes from "./cfg__accounts__user_profile/models";
export * as CfgAccountsTypes from "./cfg__accounts/models";
export * as CfgCentrifugoTypes from "./cfg__centrifugo/models";
export * as CfgEndpointsTypes from "./cfg__endpoints/models";
export * as CfgGrpcMonitoringTypes from "./cfg__grpc__grpc_monitoring/models";
export * as CfgHealthTypes from "./cfg__health/models";
export * as CfgKnowbaseTypes from "./cfg__knowbase/models";
export * as CfgLeadsTypes from "./cfg__leads/models";
export * as CfgNewsletterTypes from "./cfg__newsletter/models";
export * as CfgPaymentsTypes from "./cfg__payments/models";
export * as CfgSupportTypes from "./cfg__support/models";
export * as Enums from "./enums";

// Re-export Zod schemas for runtime validation
export * as Schemas from "./_utils/schemas";

// Re-export typed fetchers for universal usage
export * as Fetchers from "./_utils/fetchers";
export * from "./_utils/fetchers";

// Re-export API instance configuration functions
export {
  configureAPI,
  getAPIInstance,
  reconfigureAPI,
  clearAPITokens,
  resetAPI,
  isAPIConfigured
} from "./api-instance";

// Re-export SWR hooks for React
export * as Hooks from "./_utils/hooks";

// Re-export core client
export { APIClient };

// Re-export OpenAPI schema
export { OPENAPI_SCHEMA };

// Re-export storage adapters for convenience
export type { StorageAdapter };
export { LocalStorageAdapter, CookieStorageAdapter, MemoryStorageAdapter };

// Re-export error classes for convenience
export { APIError, NetworkError } from "./errors";

// Re-export HTTP adapters for custom implementations
export type { HttpClientAdapter, HttpRequest, HttpResponse } from "./http";
export { FetchAdapter } from "./http";

// Re-export logger types and classes
export type { LoggerConfig, RequestLog, ResponseLog, ErrorLog } from "./logger";
export { APILogger } from "./logger";

// Re-export retry configuration and utilities
export type { RetryConfig, FailedAttemptInfo } from "./retry";
export { withRetry, shouldRetry, DEFAULT_RETRY_CONFIG } from "./retry";

export const TOKEN_KEY = "auth_token";
export const REFRESH_TOKEN_KEY = "refresh_token";

export interface APIOptions {
  /** Custom storage adapter (defaults to LocalStorageAdapter) */
  storage?: StorageAdapter;
  /** Retry configuration for failed requests */
  retryConfig?: RetryConfig;
  /** Logger configuration */
  loggerConfig?: Partial<LoggerConfig>;
}

export class API {
  private baseUrl: string;
  private _client: APIClient;
  private _token: string | null = null;
  private _refreshToken: string | null = null;
  private storage: StorageAdapter;
  private options?: APIOptions;

  // Sub-clients
  public cfg_auth!: CfgAuth;
  public cfg_bulk_email!: CfgBulkEmail;
  public cfg_campaigns!: CfgCampaigns;
  public cfg_centrifugo_admin_api!: CfgCentrifugoAdminApi;
  public cfg_centrifugo_monitoring!: CfgCentrifugoMonitoring;
  public cfg_centrifugo_testing!: CfgCentrifugoTesting;
  public cfg_dashboard_api_zones!: CfgDashboardApiZones;
  public cfg_dashboard_activity!: CfgDashboardActivity;
  public cfg_dashboard_charts!: CfgDashboardCharts;
  public cfg_dashboard_commands!: CfgDashboardCommands;
  public cfg_dashboard_overview!: CfgDashboardOverview;
  public cfg_dashboard_statistics!: CfgDashboardStatistics;
  public cfg_dashboard_system!: CfgDashboardSystem;
  public cfg_lead_submission!: CfgLeadSubmission;
  public cfg_logs!: CfgLogs;
  public cfg_newsletters!: CfgNewsletters;
  public cfg_rq_jobs!: CfgRqJobs;
  public cfg_rq_monitoring!: CfgRqMonitoring;
  public cfg_rq_queues!: CfgRqQueues;
  public cfg_rq_registries!: CfgRqRegistries;
  public cfg_rq_schedules!: CfgRqSchedules;
  public cfg_rq_testing!: CfgRqTesting;
  public cfg_rq_workers!: CfgRqWorkers;
  public cfg_subscriptions!: CfgSubscriptions;
  public cfg_testing!: CfgTesting;
  public cfg_user_profile!: CfgUserProfile;
  public cfg_accounts!: CfgAccounts;
  public cfg_centrifugo!: CfgCentrifugo;
  public cfg_endpoints!: CfgEndpoints;
  public cfg_grpc_monitoring!: CfgGrpcMonitoring;
  public cfg_health!: CfgHealth;
  public cfg_knowbase!: CfgKnowbase;
  public cfg_leads!: CfgLeads;
  public cfg_newsletter!: CfgNewsletter;
  public cfg_payments!: CfgPayments;
  public cfg_support!: CfgSupport;

  constructor(baseUrl: string, options?: APIOptions) {
    this.baseUrl = baseUrl;
    this.options = options;

    // Create logger if config provided
    const logger = options?.loggerConfig ? new APILogger(options.loggerConfig) : undefined;

    // Initialize storage with logger
    this.storage = options?.storage || new LocalStorageAdapter(logger);

    this._loadTokensFromStorage();

    // Initialize APIClient
    this._client = new APIClient(this.baseUrl, {
      retryConfig: this.options?.retryConfig,
      loggerConfig: this.options?.loggerConfig,
    });

    // Always inject auth header wrapper (reads token dynamically from storage)
    this._injectAuthHeader();

    // Initialize sub-clients from APIClient
    this.cfg_auth = this._client.cfg_auth;
    this.cfg_bulk_email = this._client.cfg_bulk_email;
    this.cfg_campaigns = this._client.cfg_campaigns;
    this.cfg_centrifugo_admin_api = this._client.cfg_centrifugo_admin_api;
    this.cfg_centrifugo_monitoring = this._client.cfg_centrifugo_monitoring;
    this.cfg_centrifugo_testing = this._client.cfg_centrifugo_testing;
    this.cfg_dashboard_api_zones = this._client.cfg_dashboard_api_zones;
    this.cfg_dashboard_activity = this._client.cfg_dashboard_activity;
    this.cfg_dashboard_charts = this._client.cfg_dashboard_charts;
    this.cfg_dashboard_commands = this._client.cfg_dashboard_commands;
    this.cfg_dashboard_overview = this._client.cfg_dashboard_overview;
    this.cfg_dashboard_statistics = this._client.cfg_dashboard_statistics;
    this.cfg_dashboard_system = this._client.cfg_dashboard_system;
    this.cfg_lead_submission = this._client.cfg_lead_submission;
    this.cfg_logs = this._client.cfg_logs;
    this.cfg_newsletters = this._client.cfg_newsletters;
    this.cfg_rq_jobs = this._client.cfg_rq_jobs;
    this.cfg_rq_monitoring = this._client.cfg_rq_monitoring;
    this.cfg_rq_queues = this._client.cfg_rq_queues;
    this.cfg_rq_registries = this._client.cfg_rq_registries;
    this.cfg_rq_schedules = this._client.cfg_rq_schedules;
    this.cfg_rq_testing = this._client.cfg_rq_testing;
    this.cfg_rq_workers = this._client.cfg_rq_workers;
    this.cfg_subscriptions = this._client.cfg_subscriptions;
    this.cfg_testing = this._client.cfg_testing;
    this.cfg_user_profile = this._client.cfg_user_profile;
    this.cfg_accounts = this._client.cfg_accounts;
    this.cfg_centrifugo = this._client.cfg_centrifugo;
    this.cfg_endpoints = this._client.cfg_endpoints;
    this.cfg_grpc_monitoring = this._client.cfg_grpc_monitoring;
    this.cfg_health = this._client.cfg_health;
    this.cfg_knowbase = this._client.cfg_knowbase;
    this.cfg_leads = this._client.cfg_leads;
    this.cfg_newsletter = this._client.cfg_newsletter;
    this.cfg_payments = this._client.cfg_payments;
    this.cfg_support = this._client.cfg_support;
  }

  private _loadTokensFromStorage(): void {
    this._token = this.storage.getItem(TOKEN_KEY);
    this._refreshToken = this.storage.getItem(REFRESH_TOKEN_KEY);
  }

  private _reinitClients(): void {
    this._client = new APIClient(this.baseUrl, {
      retryConfig: this.options?.retryConfig,
      loggerConfig: this.options?.loggerConfig,
    });

    // Always inject auth header wrapper (reads token dynamically from storage)
    this._injectAuthHeader();

    // Reinitialize sub-clients
    this.cfg_auth = this._client.cfg_auth;
    this.cfg_bulk_email = this._client.cfg_bulk_email;
    this.cfg_campaigns = this._client.cfg_campaigns;
    this.cfg_centrifugo_admin_api = this._client.cfg_centrifugo_admin_api;
    this.cfg_centrifugo_monitoring = this._client.cfg_centrifugo_monitoring;
    this.cfg_centrifugo_testing = this._client.cfg_centrifugo_testing;
    this.cfg_dashboard_api_zones = this._client.cfg_dashboard_api_zones;
    this.cfg_dashboard_activity = this._client.cfg_dashboard_activity;
    this.cfg_dashboard_charts = this._client.cfg_dashboard_charts;
    this.cfg_dashboard_commands = this._client.cfg_dashboard_commands;
    this.cfg_dashboard_overview = this._client.cfg_dashboard_overview;
    this.cfg_dashboard_statistics = this._client.cfg_dashboard_statistics;
    this.cfg_dashboard_system = this._client.cfg_dashboard_system;
    this.cfg_lead_submission = this._client.cfg_lead_submission;
    this.cfg_logs = this._client.cfg_logs;
    this.cfg_newsletters = this._client.cfg_newsletters;
    this.cfg_rq_jobs = this._client.cfg_rq_jobs;
    this.cfg_rq_monitoring = this._client.cfg_rq_monitoring;
    this.cfg_rq_queues = this._client.cfg_rq_queues;
    this.cfg_rq_registries = this._client.cfg_rq_registries;
    this.cfg_rq_schedules = this._client.cfg_rq_schedules;
    this.cfg_rq_testing = this._client.cfg_rq_testing;
    this.cfg_rq_workers = this._client.cfg_rq_workers;
    this.cfg_subscriptions = this._client.cfg_subscriptions;
    this.cfg_testing = this._client.cfg_testing;
    this.cfg_user_profile = this._client.cfg_user_profile;
    this.cfg_accounts = this._client.cfg_accounts;
    this.cfg_centrifugo = this._client.cfg_centrifugo;
    this.cfg_endpoints = this._client.cfg_endpoints;
    this.cfg_grpc_monitoring = this._client.cfg_grpc_monitoring;
    this.cfg_health = this._client.cfg_health;
    this.cfg_knowbase = this._client.cfg_knowbase;
    this.cfg_leads = this._client.cfg_leads;
    this.cfg_newsletter = this._client.cfg_newsletter;
    this.cfg_payments = this._client.cfg_payments;
    this.cfg_support = this._client.cfg_support;
  }

  private _injectAuthHeader(): void {
    // Override request method to inject auth header
    const originalRequest = this._client.request.bind(this._client);
    this._client.request = async <T>(
      method: string,
      path: string,
      options?: { params?: Record<string, any>; body?: any; formData?: FormData; headers?: Record<string, string> }
    ): Promise<T> => {
      // Read token from storage dynamically (supports JWT injection after instantiation)
      const token = this.getToken();
      const mergedOptions = {
        ...options,
        headers: {
          ...(options?.headers || {}),
          ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        },
      };

      return originalRequest(method, path, mergedOptions);
    };
  }

  /**
   * Get current JWT token
   */
  getToken(): string | null {
    return this.storage.getItem(TOKEN_KEY);
  }

  /**
   * Get current refresh token
   */
  getRefreshToken(): string | null {
    return this.storage.getItem(REFRESH_TOKEN_KEY);
  }

  /**
   * Set JWT token and refresh token
   * @param token - JWT access token
   * @param refreshToken - JWT refresh token (optional)
   */
  setToken(token: string, refreshToken?: string): void {
    this._token = token;
    this.storage.setItem(TOKEN_KEY, token);

    if (refreshToken) {
      this._refreshToken = refreshToken;
      this.storage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    }

    // Reinitialize clients with new token
    this._reinitClients();
  }

  /**
   * Clear all tokens
   */
  clearTokens(): void {
    this._token = null;
    this._refreshToken = null;
    this.storage.removeItem(TOKEN_KEY);
    this.storage.removeItem(REFRESH_TOKEN_KEY);

    // Reinitialize clients without token
    this._reinitClients();
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  /**
   * Update base URL and reinitialize clients
   * @param url - New base URL
   */
  setBaseUrl(url: string): void {
    this.baseUrl = url;
    this._reinitClients();
  }

  /**
   * Get current base URL
   */
  getBaseUrl(): string {
    return this.baseUrl;
  }

  /**
   * Get OpenAPI schema
   * @returns Complete OpenAPI specification for this API
   */
  getSchema(): any {
    return OPENAPI_SCHEMA;
  }
}

export default API;
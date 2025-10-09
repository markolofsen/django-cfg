/**
 * Django CFG Sample API - API Client with JWT Management
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
export * as CfgAuthTypes from "./cfg__cfg__auth/models";
export * as CfgBulkEmailTypes from "./cfg__cfg__bulk_email/models";
export * as CfgCampaignsTypes from "./cfg__cfg__campaigns/models";
export * as CfgLeadSubmissionTypes from "./cfg__cfg__lead_submission/models";
export * as CfgLogsTypes from "./cfg__cfg__logs/models";
export * as CfgNewslettersTypes from "./cfg__cfg__newsletters/models";
export * as CfgSubscriptionsTypes from "./cfg__cfg__subscriptions/models";
export * as CfgTestingTypes from "./cfg__cfg__testing/models";
export * as CfgUserProfileTypes from "./cfg__cfg__user_profile/models";
export * as CfgWebhooksTypes from "./cfg__cfg__webhooks/models";
export * as CfgAccountsTypes from "./cfg__cfg__cfg__accounts/models";
export * as CfgEndpointsTypes from "./cfg__cfg__cfg__endpoints/models";
export * as CfgHealthTypes from "./cfg__cfg__cfg__health/models";
export * as CfgLeadsTypes from "./cfg__cfg__cfg__leads/models";
export * as CfgNewsletterTypes from "./cfg__cfg__cfg__newsletter/models";
export * as CfgPaymentsTypes from "./cfg__cfg__cfg__payments/models";
export * as CfgSupportTypes from "./cfg__cfg__cfg__support/models";
export * as CfgTasksTypes from "./cfg__cfg__cfg__tasks/models";
export * as Enums from "./enums";

// Re-export Zod schemas for runtime validation
export * as Schemas from "./_utils/schemas";

// Re-export typed fetchers for universal usage
export * as Fetchers from "./_utils/fetchers";

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
  private _client!: APIClient;
  private _token: string | null = null;
  private _refreshToken: string | null = null;
  private storage: StorageAdapter;
  private options?: APIOptions;

  // Sub-clients
  public cfg_auth!: APIClient['cfg_auth'];
  public cfg_bulk_email!: APIClient['cfg_bulk_email'];
  public cfg_campaigns!: APIClient['cfg_campaigns'];
  public cfg_lead_submission!: APIClient['cfg_lead_submission'];
  public cfg_logs!: APIClient['cfg_logs'];
  public cfg_newsletters!: APIClient['cfg_newsletters'];
  public cfg_subscriptions!: APIClient['cfg_subscriptions'];
  public cfg_testing!: APIClient['cfg_testing'];
  public cfg_user_profile!: APIClient['cfg_user_profile'];
  public cfg_webhooks!: APIClient['cfg_webhooks'];
  public cfg__accounts!: APIClient['cfg__accounts'];
  public cfg__endpoints!: APIClient['cfg__endpoints'];
  public cfg__health!: APIClient['cfg__health'];
  public cfg__leads!: APIClient['cfg__leads'];
  public cfg__newsletter!: APIClient['cfg__newsletter'];
  public cfg__payments!: APIClient['cfg__payments'];
  public cfg__support!: APIClient['cfg__support'];
  public cfg__tasks!: APIClient['cfg__tasks'];

  constructor(baseUrl: string, options?: APIOptions) {
    this.baseUrl = baseUrl;
    this.options = options;

    // Create logger if config provided
    const logger = options?.loggerConfig ? new APILogger(options.loggerConfig) : undefined;

    // Initialize storage with logger
    this.storage = options?.storage || new LocalStorageAdapter(logger);

    this._loadTokensFromStorage();
    this._initClients();
  }

  private _loadTokensFromStorage(): void {
    this._token = this.storage.getItem(TOKEN_KEY);
    this._refreshToken = this.storage.getItem(REFRESH_TOKEN_KEY);
  }

  private _initClients(): void {
    this._client = new APIClient(this.baseUrl, {
      retryConfig: (this as any).options?.retryConfig,
      loggerConfig: (this as any).options?.loggerConfig,
    });

    // Inject Authorization header if token exists
    if (this._token) {
      this._injectAuthHeader();
    }

    // Proxy sub-clients
    this.cfg_auth = this._client.cfg_auth;
    this.cfg_bulk_email = this._client.cfg_bulk_email;
    this.cfg_campaigns = this._client.cfg_campaigns;
    this.cfg_lead_submission = this._client.cfg_lead_submission;
    this.cfg_logs = this._client.cfg_logs;
    this.cfg_newsletters = this._client.cfg_newsletters;
    this.cfg_subscriptions = this._client.cfg_subscriptions;
    this.cfg_testing = this._client.cfg_testing;
    this.cfg_user_profile = this._client.cfg_user_profile;
    this.cfg_webhooks = this._client.cfg_webhooks;
    this.cfg__accounts = this._client.cfg__accounts;
    this.cfg__endpoints = this._client.cfg__endpoints;
    this.cfg__health = this._client.cfg__health;
    this.cfg__leads = this._client.cfg__leads;
    this.cfg__newsletter = this._client.cfg__newsletter;
    this.cfg__payments = this._client.cfg__payments;
    this.cfg__support = this._client.cfg__support;
    this.cfg__tasks = this._client.cfg__tasks;
  }

  private _injectAuthHeader(): void {
    // Override request method to inject auth header
    const originalRequest = this._client.request.bind(this._client);
    this._client.request = async <T>(
      method: string,
      path: string,
      options?: { params?: Record<string, any>; body?: any }
    ): Promise<T> => {
      const headers: Record<string, string> = {};

      if (this._token) {
        headers['Authorization'] = `Bearer ${this._token}`;
      }

      // Merge with existing options
      const mergedOptions = {
        ...options,
        headers: {
          ...(options as any)?.headers,
          ...headers,
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
    this._initClients();
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
    this._initClients();
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
    this._initClients();
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
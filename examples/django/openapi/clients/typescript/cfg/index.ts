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
 * // Custom storage (for Electron/Node.js)
 * import { MemoryStorageAdapter } from './storage';
 * const api = new API('https://api.example.com', {
 *   storage: new MemoryStorageAdapter()
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
export * as CfgAuthTypes from "./cfg__accounts__auth/models";
export * as CfgBulkEmailTypes from "./cfg__newsletter__bulk_email/models";
export * as CfgCampaignsTypes from "./cfg__newsletter__campaigns/models";
export * as CfgLeadSubmissionTypes from "./cfg__leads__lead_submission/models";
export * as CfgLogsTypes from "./cfg__newsletter__logs/models";
export * as CfgNewslettersTypes from "./cfg__newsletter__newsletters/models";
export * as CfgSubscriptionsTypes from "./cfg__newsletter__subscriptions/models";
export * as CfgTestingTypes from "./cfg__newsletter__testing/models";
export * as CfgUserProfileTypes from "./cfg__accounts__user_profile/models";
export * as CfgWebhooksTypes from "./cfg__payments__webhooks/models";
export * as CfgAccountsTypes from "./cfg__accounts/models";
export * as CfgLeadsTypes from "./cfg__leads/models";
export * as CfgNewsletterTypes from "./cfg__newsletter/models";
export * as CfgSupportTypes from "./cfg__support/models";
export * as CfgPaymentsTypes from "./cfg__payments/models";
export * as CfgTasksTypes from "./cfg__tasks/models";
export * as Enums from "./enums";

// Re-export storage adapters for convenience
export {
  StorageAdapter,
  LocalStorageAdapter,
  CookieStorageAdapter,
  MemoryStorageAdapter
};

export const TOKEN_KEY = "auth_token";
export const REFRESH_TOKEN_KEY = "refresh_token";

export interface APIOptions {
  /** Custom storage adapter (defaults to LocalStorageAdapter) */
  storage?: StorageAdapter;
}

export class API {
  private baseUrl: string;
  private _client!: APIClient;
  private _token: string | null = null;
  private _refreshToken: string | null = null;
  private storage: StorageAdapter;

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
  public cfg_accounts!: APIClient['cfg_accounts'];
  public cfg_leads!: APIClient['cfg_leads'];
  public cfg_newsletter!: APIClient['cfg_newsletter'];
  public cfg_support!: APIClient['cfg_support'];
  public cfg_payments!: APIClient['cfg_payments'];
  public cfg_tasks!: APIClient['cfg_tasks'];

  constructor(baseUrl: string, options?: APIOptions) {
    this.baseUrl = baseUrl;
    this.storage = options?.storage || new LocalStorageAdapter();
    this._loadTokensFromStorage();
    this._initClients();
  }

  private _loadTokensFromStorage(): void {
    this._token = this.storage.getItem(TOKEN_KEY);
    this._refreshToken = this.storage.getItem(REFRESH_TOKEN_KEY);
  }

  private _initClients(): void {
    this._client = new APIClient(this.baseUrl);

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
    this.cfg_accounts = this._client.cfg_accounts;
    this.cfg_leads = this._client.cfg_leads;
    this.cfg_newsletter = this._client.cfg_newsletter;
    this.cfg_support = this._client.cfg_support;
    this.cfg_payments = this._client.cfg_payments;
    this.cfg_tasks = this._client.cfg_tasks;
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
/**
 * BaseClient for Django-CFG API
 *
 * Base class for all Django-CFG services with unified API access.
 *
 * Architecture:
 * - Accounts: Authentication, user profiles
 * - Tasks: Task management and monitoring
 * - Payments: Payment processing and webhooks
 * - Newsletter: Email campaigns, subscriptions, bulk emails
 * - Knowbase: Knowledge base management
 * - Leads: Lead capture and management
 * - Support: Support tickets
 * - Centrifugo: Real-time notifications and monitoring
 *
 * Uses generated TypeScript client with full type safety.
 */

import { API, LocalStorageAdapter } from './generated/cfg';
import { APIError } from './generated/cfg/errors';
import { settings } from '@/core/settings';


// Get API URL from environment
const apiUrl = settings.api.baseUrl;
const storage = {
  storage: new LocalStorageAdapter(),
}

// Create singleton CFG API instance
const api = new API(apiUrl, storage);

export class BaseClient {
  /**
   * Django-CFG API client
   *
   * Available endpoints:
   * - this.cfgApi.cfg_accounts - User accounts
   * - this.cfgApi.cfg_accounts_auth - Authentication
   * - this.cfgApi.cfg_accounts_user_profile - User profiles
   * - this.cfgApi.cfg_tasks - Task management
   * - this.cfgApi.cfg_payments - Payments
   * - this.cfgApi.cfg_newsletter - Newsletter
   * - this.cfgApi.cfg_newsletter_bulk_email - Bulk emails
   * - this.cfgApi.cfg_newsletter_campaigns - Email campaigns
   * - this.cfgApi.cfg_newsletter_subscriptions - Subscriptions
   * - this.cfgApi.cfg_knowbase - Knowledge base
   * - this.cfgApi.cfg_leads - Lead management
   * - this.cfgApi.cfg_leads_lead_submission - Lead submission
   * - this.cfgApi.cfg_support - Support tickets
   * - this.cfgApi.cfg_centrifugo_centrifugo_admin_api - Centrifugo admin
   * - this.cfgApi.cfg_centrifugo_centrifugo_monitoring - Centrifugo monitoring
   * - this.cfgApi.cfg_health - Health checks
   * - this.cfgApi.cfg_endpoints - Endpoints listing
   */
  protected static api = api;
}

// Export API instance and error classes
export { api, APIError };

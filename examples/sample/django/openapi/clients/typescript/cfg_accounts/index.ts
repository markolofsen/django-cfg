/**
 * Accounts API - Index
 * User management, OTP, profiles, and activity tracking API
 *
 * Zone: cfg_accounts
 * Apps: django_cfg.apps.accounts
 */

export * from "./sdk.gen";
export * from "./types.gen";
export * from "./client.gen";

// Re-export main client for convenience
export { client as default } from "./client.gen";

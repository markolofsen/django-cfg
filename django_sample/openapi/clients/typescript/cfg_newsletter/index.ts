/**
 * Newsletter API - Index
 * Email campaigns, subscriptions, and newsletter management API
 *
 * Zone: cfg_newsletter
 * Apps: django_cfg.apps.newsletter
 */

export * from "./sdk.gen";
export * from "./types.gen";
export * from "./client.gen";

// Re-export main client for convenience
export { client as default } from "./client.gen";

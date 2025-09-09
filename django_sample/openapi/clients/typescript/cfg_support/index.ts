/**
 * Support API - Index
 * Support tickets and messages API
 *
 * Zone: cfg_support
 * Apps: django_cfg.apps.support
 */

export * from "./sdk.gen";
export * from "./types.gen";
export * from "./client.gen";

// Re-export main client for convenience
export { client as default } from "./client.gen";

/**
 * Leads API - Index
 * Lead collection, contact forms, and CRM integration API
 *
 * Zone: cfg_leads
 * Apps: django_cfg.apps.leads
 */

export * from "./sdk.gen";
export * from "./types.gen";
export * from "./client.gen";

// Re-export main client for convenience
export { client as default } from "./client.gen";

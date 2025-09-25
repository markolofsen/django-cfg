/**
 * Blog API - Index
 * Blog posts and comments management
 *
 * Zone: blog
 * Apps: apps.blog
 */

export * from "./sdk.gen";
export * from "./types.gen";
export * from "./client.gen";

// Re-export main client for convenience
export { client as default } from "./client.gen";

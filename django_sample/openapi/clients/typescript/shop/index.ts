/**
 * Shop API - Index
 * E-commerce products, orders and categories
 * 
 * Zone: shop
 * Apps: apps.shop
 */

export * from './sdk.gen';
export * from './types.gen';
export * from './client.gen';

// Re-export main client for convenience
export { client as default } from './client.gen'; 
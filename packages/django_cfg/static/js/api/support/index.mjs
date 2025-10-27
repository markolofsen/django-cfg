/**
 * Support API Module
 * Re-exports the API client for convenient importing
 * @module support
 */

import { SupportAPI, supportAPI } from './client.mjs';

// Re-export the class and instance
export { SupportAPI, supportAPI };

// Default export is the instance for convenience
export default supportAPI;
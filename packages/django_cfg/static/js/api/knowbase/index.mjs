/**
 * Knowbase API Module
 * Re-exports the API client for convenient importing
 * @module knowbase
 */

import { KnowbaseAPI, knowbaseAPI } from './client.mjs';

// Re-export the class and instance
export { KnowbaseAPI, knowbaseAPI };

// Default export is the instance for convenience
export default knowbaseAPI;
/**
 * Leads API Module
 * Re-exports the API client for convenient importing
 * @module leads
 */

import { LeadsAPI, leadsAPI } from './client.mjs';

// Re-export the class and instance
export { LeadsAPI, leadsAPI };

// Default export is the instance for convenience
export default leadsAPI;
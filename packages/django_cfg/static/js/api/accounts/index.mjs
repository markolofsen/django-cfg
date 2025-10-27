/**
 * Accounts API Module
 * Re-exports the API client for convenient importing
 * @module accounts
 */

import { AccountsAPI, accountsAPI } from './client.mjs';

// Re-export the class and instance
export { AccountsAPI, accountsAPI };

// Default export is the instance for convenience
export default accountsAPI;
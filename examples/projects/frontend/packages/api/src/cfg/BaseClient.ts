/**
 * Base Client for all API services
 *
 * Provides:
 * - Centralized API instance with JWT token management
 * - LocalStorage adapter for browser environments
 * - Singleton pattern for API client
 */

import { API, LocalStorageAdapter } from './generated';

/**
 * Singleton API instance with JWT token management
 * Uses LocalStorage for token persistence
 */
const api = new API(
  typeof process !== 'undefined' && process.env?.NEXT_PUBLIC_API_URL
    ? process.env.NEXT_PUBLIC_API_URL
    : 'http://localhost:8000',
  {
    storage: new LocalStorageAdapter()
  }
);

/**
 * Base Client Class
 *
 * Service classes can extend this to access api instance
 */
export class BaseClient {
  /**
   * Authenticated API instance with JWT management
   */
  protected static api = api;
}

/**
 * Export API instance for direct access
 *
 * Usage:
 * ```typescript
 * import { api } from '@djangocfg/api';
 *
 * // Set JWT tokens after login
 * api.setToken('access-token', 'refresh-token');
 *
 * // Check authentication
 * if (api.isAuthenticated()) {
 *   // Make authenticated requests
 * }
 *
 * // Clear tokens on logout
 * api.clearTokens();
 * ```
 */
export { api };

/**
 * 
 * Request model (no read-only fields).
 */
export interface TokenRefreshRequest {
  refresh: string;
}

/**
 * 
 * Response model (includes read-only fields).
 */
export interface TokenRefresh {
  access: string;
  refresh: string;
}


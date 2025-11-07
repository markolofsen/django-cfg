/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedApiKeyList {
  /** Total number of items across all pages */
  count: number;
  /** Current page number (1-based) */
  page: number;
  /** Total number of pages */
  pages: number;
  /** Number of items per page */
  page_size: number;
  /** Whether there is a next page */
  has_next: boolean;
  /** Whether there is a previous page */
  has_previous: boolean;
  /** Next page number (null if no next page) */
  next_page?: number | null;
  /** Previous page number (null if no previous page) */
  previous_page?: number | null;
  /** Array of items for current page */
  results: Array<ApiKey>;
}

/**
 * API Key information (read-only).
 * 
 * Response model (includes read-only fields).
 */
export interface ApiKey {
  /** Database ID */
  id: number;
  /** Key name/description */
  name: string;
  /** Type of API key */
  key_type: string;
  /** Masked API key (first 4 and last 4 chars) */
  masked_key: string;
  /** Whether key is active */
  is_active: boolean;
  /** Whether key is valid (active and not expired) */
  is_valid: boolean;
  /** User ID */
  user_id: number;
  /** Username */
  username: string;
  /** User email */
  user_email: string;
  /** Total requests made with this key */
  request_count: number;
  /** When key was last used */
  last_used_at: string | null;
  /** When key expires (null = never) */
  expires_at: string | null;
  /** When key was created */
  created_at: string;
  /** User who created this key */
  created_by: string | null;
}

/**
 * API Key usage statistics.
 * 
 * Response model (includes read-only fields).
 */
export interface ApiKeyStats {
  /** Total API keys */
  total_keys: number;
  /** Active API keys */
  active_keys: number;
  /** Expired API keys */
  expired_keys: number;
  /** Total requests across all keys */
  total_requests: number;
  /** Count of keys by type */
  keys_by_type: Record<string, number>;
}


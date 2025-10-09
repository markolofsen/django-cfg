/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedNewsletterList {
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
  next_page?: number;
  /** Previous page number (null if no previous page) */
  previous_page?: number;
  /** Array of items for current page */
  results: Array<Newsletter>;
}

/**
 * Serializer for Newsletter model.
 * 
 * Response model (includes read-only fields).
 */
export interface Newsletter {
  id: number;
  title: string;
  description?: string;
  is_active?: boolean;
  /** Automatically subscribe new users to this newsletter */
  auto_subscribe?: boolean;
  created_at: string;
  updated_at: string;
  subscribers_count: number;
}


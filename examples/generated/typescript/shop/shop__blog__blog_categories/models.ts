/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedBlogCategoryList {
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
  results: Array<BlogCategory>;
}

/**
 * Serializer for blog categories.
 * 
 * Request model (no read-only fields).
 */
export interface BlogCategoryRequest {
  name: string;
  description?: string;
  /** Hex color code */
  color?: string;
  meta_title?: string;
  meta_description?: string;
  parent?: number | null;
}

/**
 * Serializer for blog categories.
 * 
 * Response model (includes read-only fields).
 */
export interface BlogCategory {
  id: number;
  name: string;
  slug: string;
  description?: string;
  /** Hex color code */
  color?: string;
  meta_title?: string;
  meta_description?: string;
  parent?: number | null;
  posts_count: number;
  children: Array<Record<string, any>>;
  created_at: string;
  updated_at: string;
}


/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedShopCategoryList {
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
  results: Array<ShopCategory>;
}

/**
 * Serializer for shop categories.
 * 
 * Response model (includes read-only fields).
 */
export interface ShopCategory {
  id: number;
  name: string;
  slug: string;
  description?: string;
  image?: string;
  parent?: number;
  meta_title?: string;
  meta_description?: string;
  products_count: number;
  children: Array<Record<string, any>>;
  is_active?: boolean;
  sort_order?: number;
  created_at: string;
  updated_at: string;
}


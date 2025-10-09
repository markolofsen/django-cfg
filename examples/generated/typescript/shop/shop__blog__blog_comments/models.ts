/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedCommentList {
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
  results: Array<Comment>;
}

/**
 * Serializer for blog comments.
 * 
 * Request model (no read-only fields).
 */
export interface CommentRequest {
  content: string;
  parent?: number;
}

/**
 * Serializer for blog comments.
 * 
 * Response model (includes read-only fields).
 */
export interface Comment {
  id: number;
  content: string;
  author: Record<string, any>;
  parent?: number;
  is_approved: boolean;
  likes_count: number;
  replies: Array<Record<string, any>>;
  can_edit: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Serializer for blog comments.
 * 
 * Request model (no read-only fields).
 */
export interface PatchedCommentRequest {
  content?: string;
  parent?: number;
}

/**
 * Serializer for post authors.
 * 
 * Response model (includes read-only fields).
 */
export interface Author {
  id: number;
  /** Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. */
  username: string;
  first_name?: string;
  last_name?: string;
  full_name: string;
  avatar?: string;
}


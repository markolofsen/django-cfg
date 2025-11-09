/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedJobListList {
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
  results: Array<JobList>;
}

/**
 * Job list item serializer. Provides basic job information for list views.
 * 
 * Request model (no read-only fields).
 */
export interface JobListRequest {
  /** Job ID */
  id: string;
  /** Function name */
  func_name: string;
  /** Job creation time */
  created_at: string;
  /** Job status (queued/started/finished/failed) */
  status: string;
  /** Queue name */
  queue: string;
  /** Job timeout in seconds */
  timeout?: number | null;
}

/**
 * Job action response serializer. Used for job management actions (requeue,
 * delete, etc.).
 * 
 * Response model (includes read-only fields).
 */
export interface JobActionResponse {
  /** Action success status */
  success: boolean;
  /** Action result message */
  message: string;
  /** Job ID */
  job_id: string;
  /** Action performed (requeue/delete/cancel) */
  action: string;
}

/**
 * Job list item serializer. Provides basic job information for list views.
 * 
 * Response model (includes read-only fields).
 */
export interface JobList {
  /** Job ID */
  id: string;
  /** Function name */
  func_name: string;
  /** Job creation time */
  created_at: string;
  /** Job status (queued/started/finished/failed) */
  status: string;
  /** Queue name */
  queue: string;
  /** Job timeout in seconds */
  timeout?: number | null;
}


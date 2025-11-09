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
 * Detailed job information serializer. Provides comprehensive job details
 * including result and metadata.
 * 
 * Response model (includes read-only fields).
 */
export interface JobDetail {
  /** Job ID */
  id: string;
  /** Function name */
  func_name: string;
  /** Function arguments */
  args?: Array<string>;
  /** Function keyword arguments */
  kwargs?: Record<string, string>;
  /** Job creation time */
  created_at: string;
  /** Job enqueue time */
  enqueued_at?: string | null;
  /** Job start time */
  started_at?: string | null;
  /** Job end time */
  ended_at?: string | null;
  /** Job status (queued/started/finished/failed) */
  status: string;
  /** Queue name */
  queue: string;
  /** Worker name if started */
  worker_name?: string | null;
  /** Job timeout in seconds */
  timeout?: number | null;
  /** Result TTL in seconds */
  result_ttl?: number | null;
  /** Failure TTL in seconds */
  failure_ttl?: number | null;
  /** Job result if finished */
  result?: string | null;
  /** Exception info if failed */
  exc_info?: string | null;
  /** Job metadata */
  meta?: Record<string, string>;
  /** List of dependency job IDs */
  dependency_ids?: Array<string>;
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


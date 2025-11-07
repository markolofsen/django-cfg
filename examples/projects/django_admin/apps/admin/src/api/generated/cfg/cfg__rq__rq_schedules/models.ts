/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedScheduledJobList {
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
  results: Array<ScheduledJob>;
}

/**
 * Serializer for creating a scheduled job. Supports three scheduling methods:
 * 1. scheduled_time: Schedule job at specific time 2. interval: Schedule job
 * to repeat at intervals 3. cron: Schedule job with cron expression
 * 
 * Request model (no read-only fields).
 */
export interface ScheduleCreateRequest {
  /** Function path (e.g., 'myapp.tasks.my_task') */
  func: string;
  /** Function arguments */
  args?: Array<string>;
  /** Function keyword arguments */
  kwargs?: Record<string, string>;
  /** Queue name to schedule job in */
  queue_name?: string;
  /** Schedule job at specific time (ISO 8601) */
  scheduled_time?: string | null;
  /** Schedule job to repeat every N seconds */
  interval?: number | null;
  /** Cron expression (e.g., '0 0 * * *' for daily at midnight) */
  cron?: string | null;
  /** Job timeout in seconds */
  timeout?: number | null;
  /** Result TTL in seconds */
  result_ttl?: number | null;
  /** Number of times to repeat (None = infinite) */
  repeat?: number | null;
  /** Job description */
  description?: string | null;
}

/**
 * Response serializer for schedule actions (create/delete).
 * 
 * Response model (includes read-only fields).
 */
export interface ScheduleActionResponse {
  /** Action success status */
  success: boolean;
  /** Action result message */
  message: string;
  /** Job ID (for create action) */
  job_id?: string | null;
  /** Action performed (create/delete/cancel) */
  action: string;
}

/**
 * Serializer for scheduled job information.
 * 
 * Response model (includes read-only fields).
 */
export interface ScheduledJob {
  /** Job ID */
  id: string;
  /** Function path */
  func: string;
  /** Function arguments */
  args?: Array<string>;
  /** Function keyword arguments */
  kwargs?: Record<string, string>;
  /** Queue name */
  queue_name: string;
  /** Next scheduled time */
  scheduled_time?: string | null;
  /** Repeat interval in seconds */
  interval?: number | null;
  /** Cron expression */
  cron?: string | null;
  /** Job timeout in seconds */
  timeout?: number | null;
  /** Result TTL in seconds */
  result_ttl?: number | null;
  /** Times to repeat (None = infinite) */
  repeat?: number | null;
  /** Job description */
  description?: string | null;
  /** Job creation time */
  created_at?: string | null;
  /** Job metadata */
  meta?: Record<string, string>;
}


import * as Enums from "../enums";

/**
 * Standard API response serializer.
 * 
 * Request model (no read-only fields).
 */
export interface APIResponseRequest {
  /** Operation success status */
  success: boolean;
  /** Success message */
  message?: string;
  /** Error message */
  error?: string;
  /** Response data */
  data?: Record<string, any>;
}

/**
 * Standard API response serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface APIResponse {
  /** Operation success status */
  success: boolean;
  /** Success message */
  message?: string;
  /** Error message */
  error?: string;
  /** Response data */
  data?: Record<string, any>;
}

/**
 * Serializer for queue management actions.
 * 
 * Request model (no read-only fields).
 */
export interface QueueActionRequest {
  /** Action to perform on queues

  * `clear` - clear
  * `clear_all` - clear_all
  * `purge` - purge
  * `purge_failed` - purge_failed
  * `flush` - flush */
  action: Enums.QueueActionRequestAction;
  /** Specific queues to target (empty = all queues) */
  queue_names?: Array<string>;
}

/**
 * Serializer for queue management actions.
 * 
 * Response model (includes read-only fields).
 */
export interface QueueAction {
  /** Action to perform on queues

  * `clear` - clear
  * `clear_all` - clear_all
  * `purge` - purge
  * `purge_failed` - purge_failed
  * `flush` - flush */
  action: Enums.QueueActionAction;
  /** Specific queues to target (empty = all queues) */
  queue_names?: Array<string>;
}

/**
 * Serializer for queue status data.
 * 
 * Response model (includes read-only fields).
 */
export interface QueueStatus {
  /** Queue information with pending/failed counts */
  queues: Record<string, any>;
  /** Number of active workers */
  workers: number;
  /** Redis connection status */
  redis_connected: boolean;
  /** Current timestamp */
  timestamp: string;
  /** Error message if any */
  error?: string;
}

/**
 * Serializer for task statistics data.
 * 
 * Response model (includes read-only fields).
 */
export interface TaskStatistics {
  /** Task count statistics */
  statistics: Record<string, any>;
  /** List of recent tasks */
  recent_tasks: Array<Record<string, any>>;
  /** Current timestamp */
  timestamp: string;
  /** Error message if any */
  error?: string;
}

/**
 * Serializer for worker management actions.
 * 
 * Request model (no read-only fields).
 */
export interface WorkerActionRequest {
  /** Action to perform on workers

  * `start` - start
  * `stop` - stop
  * `restart` - restart */
  action: Enums.WorkerActionRequestAction;
  /** Number of worker processes */
  processes?: number;
  /** Number of threads per process */
  threads?: number;
}

/**
 * Serializer for worker management actions.
 * 
 * Response model (includes read-only fields).
 */
export interface WorkerAction {
  /** Action to perform on workers

  * `start` - start
  * `stop` - stop
  * `restart` - restart */
  action: Enums.WorkerActionAction;
  /** Number of worker processes */
  processes?: number;
  /** Number of threads per process */
  threads?: number;
}


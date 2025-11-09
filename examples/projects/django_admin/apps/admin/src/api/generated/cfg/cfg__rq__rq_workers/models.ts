/**
 * Aggregated worker statistics serializer. Provides overview of all workers
 * across all queues.
 * 
 * Response model (includes read-only fields).
 */
export interface WorkerStats {
  /** Total number of workers */
  total_workers: number;
  /** Number of busy workers */
  busy_workers?: number;
  /** Number of idle workers */
  idle_workers?: number;
  /** Number of suspended workers */
  suspended_workers?: number;
  /** Total successful jobs (all workers) */
  total_successful_jobs?: number;
  /** Total failed jobs (all workers) */
  total_failed_jobs?: number;
  /** Total working time across all workers (seconds) */
  total_working_time?: number;
  /** List of individual workers */
  workers?: Array<Worker>;
}

/**
 * Worker information serializer. Provides detailed information about an RQ
 * worker.
 * 
 * Response model (includes read-only fields).
 */
export interface Worker {
  /** Worker name/ID */
  name: string;
  /** List of queue names */
  queues?: Array<string>;
  /** Worker state (idle/busy/suspended) */
  state: string;
  /** Current job ID if busy */
  current_job?: string | null;
  /** Worker start time */
  birth: string;
  /** Last heartbeat timestamp */
  last_heartbeat: string;
  /** Total successful jobs */
  successful_job_count?: number;
  /** Total failed jobs */
  failed_job_count?: number;
  /** Total working time in seconds */
  total_working_time?: number;
}


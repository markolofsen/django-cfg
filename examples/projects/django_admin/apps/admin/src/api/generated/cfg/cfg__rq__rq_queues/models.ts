/**
 * Detailed queue information serializer. Provides comprehensive queue
 * statistics and metadata.
 * 
 * Response model (includes read-only fields).
 */
export interface QueueDetail {
  /** Queue name */
  name: string;
  /** Total jobs in queue */
  count: number;
  /** Jobs waiting to be processed */
  queued_jobs?: number;
  /** Jobs currently being processed */
  started_jobs?: number;
  /** Completed jobs */
  finished_jobs?: number;
  /** Failed jobs */
  failed_jobs?: number;
  /** Deferred jobs */
  deferred_jobs?: number;
  /** Scheduled jobs */
  scheduled_jobs?: number;
  /** Number of workers for this queue */
  workers?: number;
  /** Timestamp of oldest job in queue */
  oldest_job_timestamp?: string | null;
  /** Redis connection parameters */
  connection_kwargs?: Record<string, string>;
  /** Queue is in async mode */
  is_async?: boolean;
}


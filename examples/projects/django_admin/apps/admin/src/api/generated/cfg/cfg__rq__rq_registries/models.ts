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


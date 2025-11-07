import * as Enums from "../enums";

/**
 * Serializer for testing action responses.
 * 
 * Response model (includes read-only fields).
 */
export interface TestingActionResponse {
  /** Action success status */
  success: boolean;
  /** Action message */
  message: string;
  /** Created job IDs */
  job_ids?: Array<string>;
  /** Number of items affected */
  count?: number | null;
  /** Additional metadata */
  metadata?: Record<string, string>;
}

/**
 * Serializer for running demo tasks.
 * 
 * Request model (no read-only fields).
 */
export interface RunDemoRequestRequest {
  /** Demo scenario to run

  * `success` - success
  * `failure` - failure
  * `slow` - slow
  * `progress` - progress
  * `retry` - retry
  * `random` - random
  * `memory` - memory
  * `cpu` - cpu */
  scenario: Enums.RunDemoRequestRequestScenario;
  /** Queue name */
  queue?: string;
  /** Task arguments */
  args?: Array<string>;
  /** Task keyword arguments */
  kwargs?: Record<string, string>;
  /** Job timeout in seconds */
  timeout?: number | null;
}

/**
 * Serializer for stress testing.
 * 
 * Request model (no read-only fields).
 */
export interface StressTestRequestRequest {
  /** Number of jobs to create */
  num_jobs?: number;
  /** Queue name */
  queue?: string;
  /** Task scenario

  * `success` - success
  * `failure` - failure
  * `slow` - slow
  * `random` - random */
  scenario?: Enums.StressTestRequestRequestScenario;
  /** Task duration in seconds */
  duration?: number;
}


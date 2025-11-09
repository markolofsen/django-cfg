/**
 * Request to call a gRPC method (for future implementation).
 * 
 * Request model (no read-only fields).
 */
export interface GRPCCallRequestRequest {
  /** Service name to call */
  service: string;
  /** Method name to call */
  method: string;
  /** Request payload */
  payload: Record<string, string>;
  /** Request metadata (headers) */
  metadata?: Record<string, string>;
  /** Request timeout in milliseconds */
  timeout_ms?: number;
}

/**
 * Response from calling a gRPC method.
 * 
 * Response model (includes read-only fields).
 */
export interface GRPCCallResponse {
  /** Whether call was successful */
  success: boolean;
  /** Request ID for tracking */
  request_id: string;
  /** Service name */
  service: string;
  /** Method name */
  method: string;
  /** Request status */
  status: string;
  /** gRPC status code */
  grpc_status_code: string;
  /** Call duration in milliseconds */
  duration_ms: number;
  /** Response data if successful (JSON string) */
  response?: string | null;
  /** Error message if failed */
  error?: string | null;
  /** Response metadata */
  metadata?: Record<string, string>;
  /** Response timestamp (ISO format) */
  timestamp: string;
}

/**
 * List of examples response.
 * 
 * Response model (includes read-only fields).
 */
export interface GRPCExamplesList {
  /** List of examples */
  examples?: Array<GRPCExample>;
  /** Total number of examples */
  total_examples: number;
}

/**
 * Single test log entry.
 * 
 * Response model (includes read-only fields).
 */
export interface GRPCTestLog {
  /** Request ID */
  request_id: string;
  /** Service name */
  service: string;
  /** Method name */
  method: string;
  /** Request status (success, error, etc.) */
  status: string;
  /** gRPC status code if available */
  grpc_status_code?: string | null;
  /** Error message if failed */
  error_message?: string | null;
  /** Duration in milliseconds */
  duration_ms?: number | null;
  /** Request timestamp (ISO format) */
  created_at: string;
  /** User who made the request */
  user?: string | null;
}

/**
 * Example payload for a gRPC method.
 * 
 * Response model (includes read-only fields).
 */
export interface GRPCExample {
  /** Service name */
  service: string;
  /** Method name */
  method: string;
  /** Method description */
  description: string;
  /** Example request payload */
  payload_example: Record<string, string>;
  /** Example expected response */
  expected_response: Record<string, string>;
  /** Example metadata (headers) */
  metadata_example?: Record<string, string>;
}


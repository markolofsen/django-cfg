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
  payload: Record<string, any>;
  /** Request metadata (headers) */
  metadata?: Record<string, any>;
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
  metadata?: Record<string, any>;
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
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedGRPCTestLogList {
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
  results: Array<GRPCTestLog>;
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
  payload_example: Record<string, any>;
  /** Example expected response */
  expected_response: Record<string, any>;
  /** Example metadata (headers) */
  metadata_example?: Record<string, any>;
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


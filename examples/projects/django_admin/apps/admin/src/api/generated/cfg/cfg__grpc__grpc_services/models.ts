/**
 * 
 * Response model (includes read-only fields).
 */
export interface PaginatedServiceSummaryList {
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
  results: Array<ServiceSummary>;
}

/**
 * Detailed information about a service.
 * 
 * Response model (includes read-only fields).
 */
export interface ServiceDetail {
  /** Service name */
  name: string;
  /** Full service name with package */
  full_name: string;
  /** Package name */
  package: string;
  /** Service description from docstring */
  description?: string;
  /** Path to service file */
  file_path?: string;
  /** Service class name */
  class_name: string;
  /** Base class name */
  base_class?: string;
  /** Service methods */
  methods?: Array<MethodInfo>;
  stats: Record<string, any>;
  /** Recent errors */
  recent_errors?: Array<RecentError>;
}

/**
 * List of methods for a service.
 * 
 * Response model (includes read-only fields).
 */
export interface ServiceMethods {
  /** Service name */
  service_name: string;
  /** List of methods */
  methods?: Array<MethodSummary>;
  /** Total number of methods */
  total_methods: number;
}

/**
 * Summary information for a single service.
 * 
 * Response model (includes read-only fields).
 */
export interface ServiceSummary {
  /** Service name (e.g., myapp.UserService) */
  name: string;
  /** Full service name with package */
  full_name: string;
  /** Package name */
  package: string;
  /** Number of methods in service */
  methods_count: number;
  /** Total requests to this service */
  total_requests?: number;
  /** Success rate percentage */
  success_rate?: number;
  /** Average duration in milliseconds */
  avg_duration_ms?: number;
  /** Last activity timestamp */
  last_activity_at?: string | null;
}

/**
 * Information about a service method.
 * 
 * Response model (includes read-only fields).
 */
export interface MethodInfo {
  /** Method name */
  name: string;
  /** Full method name (/service/method) */
  full_name: string;
  /** Request message type */
  request_type?: string;
  /** Response message type */
  response_type?: string;
  /** Whether method uses streaming */
  streaming?: boolean;
  /** Whether authentication is required */
  auth_required?: boolean;
}

/**
 * Service statistics.
 * 
 * Response model (includes read-only fields).
 */
export interface ServiceStats {
  /** Total requests */
  total_requests?: number;
  /** Successful requests */
  successful?: number;
  /** Failed requests */
  errors?: number;
  /** Success rate percentage */
  success_rate?: number;
  /** Average duration in milliseconds */
  avg_duration_ms?: number;
  /** Requests in last 24 hours */
  last_24h_requests?: number;
}

/**
 * Recent error information.
 * 
 * Response model (includes read-only fields).
 */
export interface RecentError {
  /** Method name where error occurred */
  method: string;
  /** Error message */
  error_message: string;
  /** gRPC status code */
  grpc_status_code: string;
  /** When error occurred (ISO timestamp) */
  occurred_at: string;
}

/**
 * Summary information for a method.
 * 
 * Response model (includes read-only fields).
 */
export interface MethodSummary {
  /** Method name */
  name: string;
  /** Full method path */
  full_name: string;
  /** Service name */
  service_name: string;
  /** Request message type */
  request_type?: string;
  /** Response message type */
  response_type?: string;
  stats: Record<string, any>;
}

/**
 * Statistics for a single gRPC method.
 * 
 * Response model (includes read-only fields).
 */
export interface MethodStats {
  /** Method name */
  method_name: string;
  /** Service name */
  service_name: string;
  /** Total requests */
  total: number;
  /** Successful requests */
  successful: number;
  /** Error requests */
  errors: number;
  /** Average duration */
  avg_duration_ms: number;
  /** Last activity timestamp */
  last_activity_at: string | null;
}


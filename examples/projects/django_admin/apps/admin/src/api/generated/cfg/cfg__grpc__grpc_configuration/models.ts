/**
 * Complete gRPC configuration response.
 * 
 * Response model (includes read-only fields).
 */
export interface GRPCConfig {
  server: GRPCServerConfig;
  framework: GRPCFrameworkConfig;
  features: GRPCFeatures;
  /** Number of registered services */
  registered_services: number;
  /** Total number of methods */
  total_methods: number;
}

/**
 * Complete gRPC server information response.
 * 
 * Response model (includes read-only fields).
 */
export interface GRPCServerInfo {
  /** Server status (running, stopped) */
  server_status: string;
  /** Server address (host:port) */
  address: string;
  /** Server start timestamp */
  started_at?: string | null;
  /** Server uptime in seconds */
  uptime_seconds?: number | null;
  /** Registered services */
  services?: Array<GRPCServiceInfo>;
  /** Active interceptors */
  interceptors?: Array<GRPCInterceptorInfo>;
  stats: GRPCStats;
}

/**
 * gRPC server configuration details.
 * 
 * Response model (includes read-only fields).
 */
export interface GRPCServerConfig {
  /** Server host address */
  host: string;
  /** Server port */
  port: number;
  /** Whether gRPC server is enabled */
  enabled: boolean;
  /** Maximum concurrent streams (async server) */
  max_concurrent_streams?: number | null;
  /** Maximum concurrent RPCs */
  max_concurrent_rpcs?: number | null;
}

/**
 * gRPC framework configuration details.
 * 
 * Response model (includes read-only fields).
 */
export interface GRPCFrameworkConfig {
  /** Whether framework is enabled */
  enabled: boolean;
  /** Auto-discover services */
  auto_discover: boolean;
  /** Services discovery path pattern */
  services_path: string;
  /** Registered interceptors */
  interceptors?: Array<string>;
}

/**
 * gRPC features configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface GRPCFeatures {
  /** API key authentication enabled */
  api_key_auth: boolean;
  /** Request logging enabled */
  request_logging: boolean;
  /** Metrics collection enabled */
  metrics: boolean;
  /** gRPC reflection enabled */
  reflection: boolean;
}

/**
 * Information about a single gRPC service.
 * 
 * Response model (includes read-only fields).
 */
export interface GRPCServiceInfo {
  /** Service name */
  name: string;
  /** Service methods */
  methods?: Array<string>;
  /** Full service name with package */
  full_name: string;
  /** Service description */
  description?: string;
}

/**
 * Information about an interceptor.
 * 
 * Response model (includes read-only fields).
 */
export interface GRPCInterceptorInfo {
  /** Interceptor name */
  name: string;
  /** Whether interceptor is enabled */
  enabled: boolean;
}

/**
 * Runtime statistics summary.
 * 
 * Response model (includes read-only fields).
 */
export interface GRPCStats {
  /** Total number of requests */
  total_requests: number;
  /** Success rate percentage */
  success_rate: number;
  /** Average duration in milliseconds */
  avg_duration_ms: number;
}


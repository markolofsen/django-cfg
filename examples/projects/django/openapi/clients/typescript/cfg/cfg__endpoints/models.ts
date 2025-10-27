/**
 * Serializer for overall endpoints status response.
 * 
 * Response model (includes read-only fields).
 */
export interface EndpointsStatus {
  /** Overall status: healthy, degraded, or unhealthy */
  status: string;
  /** Timestamp of the check */
  timestamp: string;
  /** Total number of endpoints checked */
  total_endpoints: number;
  /** Number of healthy endpoints */
  healthy: number;
  /** Number of unhealthy endpoints */
  unhealthy: number;
  /** Number of endpoints with warnings */
  warnings: number;
  /** Number of endpoints with errors */
  errors: number;
  /** Number of skipped endpoints */
  skipped: number;
  /** List of all endpoints with their status */
  endpoints: Array<Endpoint>;
}

/**
 * Serializer for URLs list response.
 * 
 * Response model (includes read-only fields).
 */
export interface URLsList {
  /** Status: success or error */
  status: string;
  /** Service name */
  service: string;
  /** Django-CFG version */
  version: string;
  /** Base URL of the service */
  base_url: string;
  /** Total number of registered URLs */
  total_urls: number;
  /** List of all registered URL patterns */
  urls: Array<URLPattern>;
}

/**
 * Serializer for single endpoint status.
 * 
 * Response model (includes read-only fields).
 */
export interface Endpoint {
  /** Resolved URL (for parametrized URLs) or URL pattern */
  url: string;
  /** Original URL pattern (for parametrized URLs) */
  url_pattern?: string | null;
  /** Django URL name (if available) */
  url_name?: string | null;
  /** URL namespace */
  namespace?: string;
  /** URL group (up to 3 depth) */
  group: string;
  /** View function/class name */
  view?: string;
  /** Status: healthy, unhealthy, warning, error, skipped, pending */
  status: string;
  /** HTTP status code */
  status_code?: number | null;
  /** Response time in milliseconds */
  response_time_ms?: number | null;
  /** Whether endpoint is healthy */
  is_healthy?: boolean | null;
  /** Error message if check failed */
  error?: string;
  /** Error type: database, general, etc. */
  error_type?: string;
  /** Reason for warning/skip */
  reason?: string;
  /** Timestamp of last check */
  last_checked?: string | null;
  /** Whether URL has parameters that were resolved with test values */
  has_parameters?: boolean;
  /** Whether endpoint required JWT authentication */
  required_auth?: boolean;
  /** Whether endpoint returned 429 (rate limited) */
  rate_limited?: boolean;
}

/**
 * Serializer for single URL pattern.
 * 
 * Response model (includes read-only fields).
 */
export interface URLPattern {
  /** URL pattern (e.g., ^api/users/(?P<pk>[^/.]+)/$) */
  pattern: string;
  /** URL name (if defined) */
  name?: string | null;
  /** Full URL name with namespace (e.g., admin:index) */
  full_name?: string | null;
  /** URL namespace */
  namespace?: string | null;
  /** View function/class name */
  view?: string | null;
  /** View class name (for CBV/ViewSets) */
  view_class?: string | null;
  /** Allowed HTTP methods */
  methods?: Array<string>;
  /** View module path */
  module?: string | null;
}


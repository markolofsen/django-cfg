/**
 * Serializer for complete config data endpoint. Returns both DjangoConfig and
 * Django settings with validation info.
 * 
 * Response model (includes read-only fields).
 */
export interface ConfigData {
  django_config: Record<string, any>;
  /** Complete Django settings (sanitized) */
  django_settings: Record<string, any>;
  _validation: Record<string, any>;
}

/**
 * Typed serializer for user's DjangoConfig settings. Reflects the actual
 * structure of DjangoConfig model. All passwords and sensitive data are
 * sanitized before reaching this serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface DjangoConfig {
  env_mode?: string | null;
  project_name?: string | null;
  project_logo?: string | null;
  project_version?: string | null;
  project_description?: string | null;
  startup_info_mode?: string | null;
  enable_support?: boolean | null;
  enable_accounts?: boolean | null;
  enable_newsletter?: boolean | null;
  enable_leads?: boolean | null;
  enable_knowbase?: boolean | null;
  enable_agents?: boolean | null;
  enable_maintenance?: boolean | null;
  enable_frontend?: boolean | null;
  enable_drf_tailwind?: boolean | null;
  site_url?: string | null;
  api_url?: string | null;
  debug?: boolean | null;
  debug_warnings?: boolean | null;
  root_urlconf?: string | null;
  wsgi_application?: string | null;
  auth_user_model?: string | null;
  project_apps?: Array<string> | null;
  databases?: Record<string, any> | null;
  redis_url?: string | null;
  cache_default?: string | null;
  cache_sessions?: string | null;
  security_domains?: Array<string> | null;
  ssl_redirect?: boolean | null;
  cors_allow_headers?: Array<string> | null;
  email?: Record<string, any> | null;
  payments?: Record<string, any> | null;
  grpc?: Record<string, any> | null;
  centrifugo?: Record<string, any> | null;
  django_rq?: Record<string, any> | null;
  drf?: Record<string, any> | null;
  spectacular?: Record<string, any> | null;
  jwt?: Record<string, any> | null;
  telegram?: Record<string, any> | null;
  ngrok?: Record<string, any> | null;
  axes?: Record<string, any> | null;
  crypto_fields?: Record<string, any> | null;
  unfold?: string | null;
  tailwind_app_name?: string | null;
  tailwind_version?: number | null;
  limits?: Record<string, any> | null;
  api_keys?: Record<string, any> | null;
  custom_middleware?: Array<string> | null;
  nextjs_admin?: Record<string, any> | null;
  admin_emails?: Array<string> | null;
  constance?: Record<string, any> | null;
  openapi_client?: Record<string, any> | null;
  _meta?: Record<string, any> | null;
}

/**
 * Validation result for config serializer.
 * 
 * Response model (includes read-only fields).
 */
export interface ConfigValidation {
  /** Validation status: 'valid', 'warning', or 'error' */
  status: string;
  /** Fields present in config but missing in serializer */
  missing_in_serializer: Array<string>;
  /** Fields present in serializer but not in config */
  extra_in_serializer: Array<string>;
  /** Fields with type mismatches */
  type_mismatches: Array<Record<string, any>>;
  /** Total fields in config */
  total_config_fields: number;
  /** Total fields in serializer */
  total_serializer_fields: number;
}

/**
 * Email configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface EmailConfig {
  backend?: string | null;
  host?: string | null;
  port?: number | null;
  username?: string | null;
  password?: string | null;
  use_tls?: boolean | null;
  use_ssl?: boolean | null;
  ssl_verify?: boolean | null;
  timeout?: number | null;
  default_from?: string | null;
}

/**
 * Payments configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface PaymentsConfig {
  enabled?: boolean | null;
  nowpayments?: Record<string, any> | null;
}

/**
 * gRPC configuration for dashboard.
 * 
 * Response model (includes read-only fields).
 */
export interface GRPCConfigDashboard {
  enabled?: boolean | null;
  host?: string | null;
  port?: number | null;
  max_workers?: number | null;
  reflection?: boolean | null;
  health_check?: boolean | null;
  interceptors?: Array<string> | null;
}

/**
 * Centrifugo configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface CentrifugoConfig {
  enabled?: boolean | null;
  api_url?: string | null;
  api_key?: string | null;
  token_hmac_secret_key?: string | null;
  timeout?: number | null;
}

/**
 * Django-RQ configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface DjangoRQConfig {
  enabled?: boolean | null;
  queues?: Array<RedisQueueConfig> | null;
  show_admin_link?: boolean | null;
  exception_handlers?: Array<string> | null;
  api_token?: string | null;
  prometheus_enabled?: boolean | null;
  schedules?: Array<Record<string, any>> | null;
}

/**
 * Django REST Framework configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface DRFConfig {
  default_pagination_class?: string | null;
  page_size?: number | null;
}

/**
 * DRF Spectacular configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface SpectacularConfig {
  title?: string | null;
  description?: string | null;
  version?: string | null;
}

/**
 * JWT configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface JWTConfig {
  access_token_lifetime?: number | null;
  refresh_token_lifetime?: number | null;
  algorithm?: string | null;
}

/**
 * Config metadata.
 * 
 * Response model (includes read-only fields).
 */
export interface ConfigMeta {
  config_class: string;
  secret_key_configured: boolean;
}

/**
 * NowPayments configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface PaymentsNowPayments {
  api_key?: string | null;
  ipn_secret?: string | null;
  sandbox?: boolean | null;
  enabled?: boolean | null;
}

/**
 * Redis Queue configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface RedisQueueConfig {
  url?: string | null;
  host?: string | null;
  port?: number | null;
  db?: number | null;
  username?: string | null;
  password?: string | null;
  default_timeout?: number | null;
  default_result_ttl?: number | null;
  sentinels?: Array<string> | null;
  master_name?: string | null;
  socket_timeout?: number | null;
}


/**
 * Serializer for complete config data endpoint. Returns both DjangoConfig and
 * Django settings with validation info.
 * 
 * Response model (includes read-only fields).
 */
export interface ConfigData {
  django_config: DjangoConfig;
  /** Complete Django settings (sanitized, contains mixed types) */
  django_settings: Record<string, string>;
  _validation: ConfigValidation;
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
  databases?: Record<string, DatabaseConfig> | null;
  redis_url?: string | null;
  cache_default?: string | null;
  cache_sessions?: string | null;
  security_domains?: Array<string> | null;
  ssl_redirect?: boolean | null;
  cors_allow_headers?: Array<string> | null;
  email?: EmailConfig | null;
  payments?: PaymentsConfig | null;
  grpc?: GRPCConfigDashboard | null;
  centrifugo?: CentrifugoConfig | null;
  django_rq?: DjangoRQConfig | null;
  drf?: DRFConfig | null;
  spectacular?: SpectacularConfig | null;
  jwt?: JWTConfig | null;
  telegram?: TelegramConfig | null;
  ngrok?: NgrokConfig | null;
  axes?: AxesConfig | null;
  crypto_fields?: Record<string, string> | null;
  unfold?: string | null;
  tailwind_app_name?: string | null;
  tailwind_version?: number | null;
  limits?: Record<string, string> | null;
  api_keys?: Record<string, string> | null;
  custom_middleware?: Array<string> | null;
  nextjs_admin?: NextJSAdminConfig | null;
  admin_emails?: Array<string> | null;
  constance?: ConstanceConfig | null;
  openapi_client?: OpenAPIClientConfig | null;
  _meta?: ConfigMeta | null;
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
  type_mismatches: Array<Record<string, string>>;
  /** Total fields in config */
  total_config_fields: number;
  /** Total fields in serializer */
  total_serializer_fields: number;
}

/**
 * Database configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface DatabaseConfig {
  engine: string;
  name: string;
  user?: string | null;
  password?: string | null;
  host?: string | null;
  port?: number | null;
  connect_timeout?: number | null;
  sslmode?: string | null;
  options?: Record<string, string> | null;
  apps?: Array<string> | null;
  operations?: Array<string> | null;
  migrate_to?: string | null;
  routing_description?: string | null;
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
  nowpayments?: PaymentsNowPayments | null;
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
  schedules?: Array<RQSchedule> | null;
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
 * Telegram service configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface TelegramConfig {
  bot_token?: string | null;
  chat_id?: number | null;
  parse_mode?: string | null;
  disable_notification?: boolean | null;
  disable_web_page_preview?: boolean | null;
  timeout?: number | null;
  webhook_url?: string | null;
  webhook_secret?: string | null;
  max_retries?: number | null;
  retry_delay?: number | null;
}

/**
 * Ngrok tunneling configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface NgrokConfig {
  enabled?: boolean | null;
  authtoken?: string | null;
  basic_auth?: Array<string> | null;
  compression?: boolean | null;
}

/**
 * Django-Axes brute-force protection configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface AxesConfig {
  enabled?: boolean | null;
  failure_limit?: number | null;
  cooloff_time?: number | null;
  lock_out_at_failure?: boolean | null;
  reset_on_success?: boolean | null;
  only_user_failures?: boolean | null;
  lockout_template?: string | null;
  lockout_url?: string | null;
  verbose?: boolean | null;
  enable_access_failure_log?: boolean | null;
  ipware_proxy_count?: number | null;
  ipware_meta_precedence_order?: Array<string> | null;
  allowed_ips?: Array<string> | null;
  denied_ips?: Array<string> | null;
  cache_name?: string | null;
  use_user_agent?: boolean | null;
  username_form_field?: string | null;
}

/**
 * Next.js Admin application configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface NextJSAdminConfig {
  enabled?: boolean | null;
  url?: string | null;
  api_base_url?: string | null;
}

/**
 * Django-Constance dynamic settings configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface ConstanceConfig {
  config?: Record<string, string> | null;
  config_fieldsets?: Record<string, string> | null;
  backend?: string | null;
  database_prefix?: string | null;
  database_cache_backend?: string | null;
  additional_config?: Record<string, string> | null;
}

/**
 * OpenAPI Client generation configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface OpenAPIClientConfig {
  enabled?: boolean | null;
  output_dir?: string | null;
  client_name?: string | null;
  schema_url?: string | null;
  generator?: string | null;
  additional_properties?: Record<string, string> | null;
  templates?: Array<string> | null;
  global_properties?: Record<string, string> | null;
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

/**
 * Redis Queue schedule configuration.
 * 
 * Response model (includes read-only fields).
 */
export interface RQSchedule {
  func?: string | null;
  cron_string?: string | null;
  queue?: string | null;
  kwargs?: Record<string, string> | null;
  args?: Array<string> | null;
  meta?: Record<string, string> | null;
  repeat?: number | null;
  result_ttl?: number | null;
}


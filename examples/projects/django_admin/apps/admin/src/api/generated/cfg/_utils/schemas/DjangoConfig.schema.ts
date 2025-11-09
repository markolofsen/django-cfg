/**
 * Zod schema for DjangoConfig
 *
 * This schema provides runtime validation and type inference.
 *  * Typed serializer for user's DjangoConfig settings.

Reflects the actual structure of DjangoConfig model.
All passwords and sensitive data are sanitized before reaching this serializer.
 *  */
import { z } from 'zod'
import { AxesConfigSchema } from './AxesConfig.schema'
import { CentrifugoConfigSchema } from './CentrifugoConfig.schema'
import { ConfigMetaSchema } from './ConfigMeta.schema'
import { ConstanceConfigSchema } from './ConstanceConfig.schema'
import { DRFConfigSchema } from './DRFConfig.schema'
import { DatabaseConfigSchema } from './DatabaseConfig.schema'
import { DjangoRQConfigSchema } from './DjangoRQConfig.schema'
import { EmailConfigSchema } from './EmailConfig.schema'
import { GRPCConfigDashboardSchema } from './GRPCConfigDashboard.schema'
import { JWTConfigSchema } from './JWTConfig.schema'
import { NextJSAdminConfigSchema } from './NextJSAdminConfig.schema'
import { NgrokConfigSchema } from './NgrokConfig.schema'
import { OpenAPIClientConfigSchema } from './OpenAPIClientConfig.schema'
import { PaymentsConfigSchema } from './PaymentsConfig.schema'
import { SpectacularConfigSchema } from './SpectacularConfig.schema'
import { TelegramConfigSchema } from './TelegramConfig.schema'

/**
 * Typed serializer for user's DjangoConfig settings.

Reflects the actual structure of DjangoConfig model.
All passwords and sensitive data are sanitized before reaching this serializer.
 */
export const DjangoConfigSchema = z.object({
  env_mode: z.string().nullable().optional(),
  project_name: z.string().nullable().optional(),
  project_logo: z.string().nullable().optional(),
  project_version: z.string().nullable().optional(),
  project_description: z.string().nullable().optional(),
  startup_info_mode: z.string().nullable().optional(),
  enable_support: z.boolean().nullable().optional(),
  enable_accounts: z.boolean().nullable().optional(),
  enable_newsletter: z.boolean().nullable().optional(),
  enable_leads: z.boolean().nullable().optional(),
  enable_knowbase: z.boolean().nullable().optional(),
  enable_agents: z.boolean().nullable().optional(),
  enable_maintenance: z.boolean().nullable().optional(),
  enable_frontend: z.boolean().nullable().optional(),
  enable_drf_tailwind: z.boolean().nullable().optional(),
  site_url: z.string().nullable().optional(),
  api_url: z.string().nullable().optional(),
  debug: z.boolean().nullable().optional(),
  debug_warnings: z.boolean().nullable().optional(),
  root_urlconf: z.string().nullable().optional(),
  wsgi_application: z.string().nullable().optional(),
  auth_user_model: z.string().nullable().optional(),
  project_apps: z.array(z.string()).nullable().optional(),
  databases: z.record(z.string(), DatabaseConfigSchema).nullable().optional(),
  redis_url: z.string().nullable().optional(),
  cache_default: z.string().nullable().optional(),
  cache_sessions: z.string().nullable().optional(),
  security_domains: z.array(z.string()).nullable().optional(),
  ssl_redirect: z.boolean().nullable().optional(),
  cors_allow_headers: z.array(z.string()).nullable().optional(),
  email: EmailConfigSchema.nullable().optional(),
  payments: PaymentsConfigSchema.nullable().optional(),
  grpc: GRPCConfigDashboardSchema.nullable().optional(),
  centrifugo: CentrifugoConfigSchema.nullable().optional(),
  django_rq: DjangoRQConfigSchema.nullable().optional(),
  drf: DRFConfigSchema.nullable().optional(),
  spectacular: SpectacularConfigSchema.nullable().optional(),
  jwt: JWTConfigSchema.nullable().optional(),
  telegram: TelegramConfigSchema.nullable().optional(),
  ngrok: NgrokConfigSchema.nullable().optional(),
  axes: AxesConfigSchema.nullable().optional(),
  crypto_fields: z.record(z.string(), z.any()).nullable().optional(),
  unfold: z.string().nullable().optional(),
  tailwind_app_name: z.string().nullable().optional(),
  tailwind_version: z.int().nullable().optional(),
  limits: z.record(z.string(), z.any()).nullable().optional(),
  api_keys: z.record(z.string(), z.any()).nullable().optional(),
  custom_middleware: z.array(z.string()).nullable().optional(),
  nextjs_admin: NextJSAdminConfigSchema.nullable().optional(),
  admin_emails: z.array(z.string()).nullable().optional(),
  constance: ConstanceConfigSchema.nullable().optional(),
  openapi_client: OpenAPIClientConfigSchema.nullable().optional(),
  _meta: ConfigMetaSchema.nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type DjangoConfig = z.infer<typeof DjangoConfigSchema>
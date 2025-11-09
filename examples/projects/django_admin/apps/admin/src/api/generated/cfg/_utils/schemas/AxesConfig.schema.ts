/**
 * Zod schema for AxesConfig
 *
 * This schema provides runtime validation and type inference.
 *  * Django-Axes brute-force protection configuration.
 *  */
import { z } from 'zod'

/**
 * Django-Axes brute-force protection configuration.
 */
export const AxesConfigSchema = z.object({
  enabled: z.boolean().nullable().optional(),
  failure_limit: z.int().nullable().optional(),
  cooloff_time: z.int().nullable().optional(),
  lock_out_at_failure: z.boolean().nullable().optional(),
  reset_on_success: z.boolean().nullable().optional(),
  only_user_failures: z.boolean().nullable().optional(),
  lockout_template: z.string().nullable().optional(),
  lockout_url: z.string().nullable().optional(),
  verbose: z.boolean().nullable().optional(),
  enable_access_failure_log: z.boolean().nullable().optional(),
  ipware_proxy_count: z.int().nullable().optional(),
  ipware_meta_precedence_order: z.array(z.string()).nullable().optional(),
  allowed_ips: z.array(z.string()).nullable().optional(),
  denied_ips: z.array(z.string()).nullable().optional(),
  cache_name: z.string().nullable().optional(),
  use_user_agent: z.boolean().nullable().optional(),
  username_form_field: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type AxesConfig = z.infer<typeof AxesConfigSchema>
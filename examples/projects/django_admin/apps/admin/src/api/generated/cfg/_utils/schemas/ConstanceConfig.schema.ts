/**
 * Zod schema for ConstanceConfig
 *
 * This schema provides runtime validation and type inference.
 *  * Django-Constance dynamic settings configuration.
 *  */
import { z } from 'zod'

/**
 * Django-Constance dynamic settings configuration.
 */
export const ConstanceConfigSchema = z.object({
  config: z.record(z.string(), z.any()).nullable().optional(),
  config_fieldsets: z.record(z.string(), z.any()).nullable().optional(),
  backend: z.string().nullable().optional(),
  database_prefix: z.string().nullable().optional(),
  database_cache_backend: z.string().nullable().optional(),
  additional_config: z.record(z.string(), z.any()).nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ConstanceConfig = z.infer<typeof ConstanceConfigSchema>
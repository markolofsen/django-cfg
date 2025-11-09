/**
 * Zod schema for ConfigMeta
 *
 * This schema provides runtime validation and type inference.
 *  * Config metadata.
 *  */
import { z } from 'zod'

/**
 * Config metadata.
 */
export const ConfigMetaSchema = z.object({
  config_class: z.string(),
  secret_key_configured: z.boolean(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ConfigMeta = z.infer<typeof ConfigMetaSchema>
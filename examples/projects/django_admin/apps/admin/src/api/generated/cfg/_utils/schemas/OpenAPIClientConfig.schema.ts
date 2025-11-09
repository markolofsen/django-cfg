/**
 * Zod schema for OpenAPIClientConfig
 *
 * This schema provides runtime validation and type inference.
 *  * OpenAPI Client generation configuration.
 *  */
import { z } from 'zod'

/**
 * OpenAPI Client generation configuration.
 */
export const OpenAPIClientConfigSchema = z.object({
  enabled: z.boolean().nullable().optional(),
  output_dir: z.string().nullable().optional(),
  client_name: z.string().nullable().optional(),
  schema_url: z.string().nullable().optional(),
  generator: z.string().nullable().optional(),
  additional_properties: z.record(z.string(), z.any()).nullable().optional(),
  templates: z.array(z.string()).nullable().optional(),
  global_properties: z.record(z.string(), z.any()).nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type OpenAPIClientConfig = z.infer<typeof OpenAPIClientConfigSchema>
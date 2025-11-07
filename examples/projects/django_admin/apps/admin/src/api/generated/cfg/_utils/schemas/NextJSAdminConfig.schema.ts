/**
 * Zod schema for NextJSAdminConfig
 *
 * This schema provides runtime validation and type inference.
 *  * Next.js Admin application configuration.
 *  */
import { z } from 'zod'

/**
 * Next.js Admin application configuration.
 */
export const NextJSAdminConfigSchema = z.object({
  enabled: z.boolean().nullable().optional(),
  url: z.string().nullable().optional(),
  api_base_url: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type NextJSAdminConfig = z.infer<typeof NextJSAdminConfigSchema>
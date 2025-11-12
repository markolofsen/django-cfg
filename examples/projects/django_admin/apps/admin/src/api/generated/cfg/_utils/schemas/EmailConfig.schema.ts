/**
 * Zod schema for EmailConfig
 *
 * This schema provides runtime validation and type inference.
 *  * Email configuration.
 *  */
import { z } from 'zod'

/**
 * Email configuration.
 */
export const EmailConfigSchema = z.object({
  backend: z.string().nullable().optional(),
  host: z.string().nullable().optional(),
  port: z.int().nullable().optional(),
  username: z.string().nullable().optional(),
  password: z.string().nullable().optional(),
  use_tls: z.boolean().nullable().optional(),
  use_ssl: z.boolean().nullable().optional(),
  ssl_verify: z.boolean().nullable().optional(),
  timeout: z.int().nullable().optional(),
  default_from: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type EmailConfig = z.infer<typeof EmailConfigSchema>
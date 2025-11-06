/**
 * Zod schema for CentrifugoConfig
 *
 * This schema provides runtime validation and type inference.
 *  * Centrifugo configuration.
 *  */
import { z } from 'zod'

/**
 * Centrifugo configuration.
 */
export const CentrifugoConfigSchema = z.object({
  enabled: z.boolean().nullable().optional(),
  api_url: z.string().nullable().optional(),
  api_key: z.string().nullable().optional(),
  token_hmac_secret_key: z.string().nullable().optional(),
  timeout: z.int().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoConfig = z.infer<typeof CentrifugoConfigSchema>
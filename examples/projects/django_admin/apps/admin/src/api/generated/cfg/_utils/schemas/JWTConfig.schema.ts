/**
 * Zod schema for JWTConfig
 *
 * This schema provides runtime validation and type inference.
 *  * JWT configuration.
 *  */
import { z } from 'zod'

/**
 * JWT configuration.
 */
export const JWTConfigSchema = z.object({
  access_token_lifetime: z.int().nullable().optional(),
  refresh_token_lifetime: z.int().nullable().optional(),
  algorithm: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type JWTConfig = z.infer<typeof JWTConfigSchema>
/**
 * Zod schema for ConnectionTokenResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Response model for connection token.
 *  */
import { z } from 'zod'

/**
 * Response model for connection token.
 */
export const ConnectionTokenResponseSchema = z.object({
  token: z.string(),
  centrifugo_url: z.string(),
  expires_at: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ConnectionTokenResponse = z.infer<typeof ConnectionTokenResponseSchema>
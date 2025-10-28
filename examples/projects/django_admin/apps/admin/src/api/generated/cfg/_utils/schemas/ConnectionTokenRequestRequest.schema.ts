/**
 * Zod schema for ConnectionTokenRequestRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Request model for connection token generation.
 *  */
import { z } from 'zod'

/**
 * Request model for connection token generation.
 */
export const ConnectionTokenRequestRequestSchema = z.object({
  user_id: z.string(),
  channels: z.array(z.string()).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ConnectionTokenRequestRequest = z.infer<typeof ConnectionTokenRequestRequestSchema>
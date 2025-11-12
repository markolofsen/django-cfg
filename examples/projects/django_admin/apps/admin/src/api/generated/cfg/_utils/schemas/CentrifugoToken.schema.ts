/**
 * Zod schema for CentrifugoToken
 *
 * This schema provides runtime validation and type inference.
 *  * Nested serializer for Centrifugo WebSocket connection token.
 *  */
import { z } from 'zod'

/**
 * Nested serializer for Centrifugo WebSocket connection token.
 */
export const CentrifugoTokenSchema = z.object({
  token: z.string(),
  centrifugo_url: z.url(),
  expires_at: z.iso.datetime(),
  channels: z.array(z.string()),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoToken = z.infer<typeof CentrifugoTokenSchema>
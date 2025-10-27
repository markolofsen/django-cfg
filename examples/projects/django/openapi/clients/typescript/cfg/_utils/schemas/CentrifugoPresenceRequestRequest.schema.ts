/**
 * Zod schema for CentrifugoPresenceRequestRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Request to get channel presence.
 *  */
import { z } from 'zod'

/**
 * Request to get channel presence.
 */
export const CentrifugoPresenceRequestRequestSchema = z.object({
  channel: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoPresenceRequestRequest = z.infer<typeof CentrifugoPresenceRequestRequestSchema>
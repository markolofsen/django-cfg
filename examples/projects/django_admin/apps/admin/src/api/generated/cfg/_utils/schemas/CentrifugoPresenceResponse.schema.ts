/**
 * Zod schema for CentrifugoPresenceResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Channel presence response.
 *  */
import { z } from 'zod'
import { CentrifugoErrorSchema } from './CentrifugoError.schema'
import { CentrifugoPresenceResultSchema } from './CentrifugoPresenceResult.schema'

/**
 * Channel presence response.
 */
export const CentrifugoPresenceResponseSchema = z.object({
  error: CentrifugoErrorSchema.optional(),
  result: CentrifugoPresenceResultSchema.optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoPresenceResponse = z.infer<typeof CentrifugoPresenceResponseSchema>
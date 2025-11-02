/**
 * Zod schema for CentrifugoPresenceStatsResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Channel presence stats response.
 *  */
import { z } from 'zod'
import { CentrifugoErrorSchema } from './CentrifugoError.schema'
import { CentrifugoPresenceStatsResultSchema } from './CentrifugoPresenceStatsResult.schema'

/**
 * Channel presence stats response.
 */
export const CentrifugoPresenceStatsResponseSchema = z.object({
  error: CentrifugoErrorSchema.optional(),
  result: CentrifugoPresenceStatsResultSchema.optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoPresenceStatsResponse = z.infer<typeof CentrifugoPresenceStatsResponseSchema>
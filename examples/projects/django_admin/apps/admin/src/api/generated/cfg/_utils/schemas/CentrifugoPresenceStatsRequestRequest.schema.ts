/**
 * Zod schema for CentrifugoPresenceStatsRequestRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Request to get channel presence statistics.
 *  */
import { z } from 'zod'

/**
 * Request to get channel presence statistics.
 */
export const CentrifugoPresenceStatsRequestRequestSchema = z.object({
  channel: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoPresenceStatsRequestRequest = z.infer<typeof CentrifugoPresenceStatsRequestRequestSchema>
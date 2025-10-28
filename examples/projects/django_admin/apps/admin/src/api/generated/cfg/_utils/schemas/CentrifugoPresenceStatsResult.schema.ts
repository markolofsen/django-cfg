/**
 * Zod schema for CentrifugoPresenceStatsResult
 *
 * This schema provides runtime validation and type inference.
 *  * Presence stats result.
 *  */
import { z } from 'zod'

/**
 * Presence stats result.
 */
export const CentrifugoPresenceStatsResultSchema = z.object({
  num_clients: z.int(),
  num_users: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoPresenceStatsResult = z.infer<typeof CentrifugoPresenceStatsResultSchema>
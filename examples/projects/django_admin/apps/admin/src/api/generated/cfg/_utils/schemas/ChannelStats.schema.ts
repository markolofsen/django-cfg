/**
 * Zod schema for ChannelStats
 *
 * This schema provides runtime validation and type inference.
 *  * Statistics per channel.
 *  */
import { z } from 'zod'

/**
 * Statistics per channel.
 */
export const ChannelStatsSchema = z.object({
  channel: z.string(),
  total: z.int(),
  successful: z.int(),
  failed: z.int(),
  avg_duration_ms: z.number(),
  avg_acks: z.number(),
  last_activity_at: z.string().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ChannelStats = z.infer<typeof ChannelStatsSchema>
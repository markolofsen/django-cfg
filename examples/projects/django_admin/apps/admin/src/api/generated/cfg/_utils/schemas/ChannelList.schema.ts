/**
 * Zod schema for ChannelList
 *
 * This schema provides runtime validation and type inference.
 *  * List of channel statistics.
 *  */
import { z } from 'zod'
import { ChannelStatsSchema } from './ChannelStats.schema'

/**
 * List of channel statistics.
 */
export const ChannelListSchema = z.object({
  channels: z.array(ChannelStatsSchema),
  total_channels: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ChannelList = z.infer<typeof ChannelListSchema>
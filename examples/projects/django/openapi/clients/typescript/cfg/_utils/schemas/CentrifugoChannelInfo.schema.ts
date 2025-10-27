/**
 * Zod schema for CentrifugoChannelInfo
 *
 * This schema provides runtime validation and type inference.
 *  * Information about a single channel.
 *  */
import { z } from 'zod'

/**
 * Information about a single channel.
 */
export const CentrifugoChannelInfoSchema = z.object({
  num_clients: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoChannelInfo = z.infer<typeof CentrifugoChannelInfoSchema>
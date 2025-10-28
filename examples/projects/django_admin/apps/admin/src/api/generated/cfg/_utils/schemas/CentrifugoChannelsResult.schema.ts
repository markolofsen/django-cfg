/**
 * Zod schema for CentrifugoChannelsResult
 *
 * This schema provides runtime validation and type inference.
 *  * Channels result wrapper.
 *  */
import { z } from 'zod'

/**
 * Channels result wrapper.
 */
export const CentrifugoChannelsResultSchema = z.object({
  channels: z.record(z.string(), z.any()),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoChannelsResult = z.infer<typeof CentrifugoChannelsResultSchema>
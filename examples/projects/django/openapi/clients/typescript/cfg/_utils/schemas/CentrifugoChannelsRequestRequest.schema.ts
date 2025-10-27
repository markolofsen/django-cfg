/**
 * Zod schema for CentrifugoChannelsRequestRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Request to list active channels.
 *  */
import { z } from 'zod'

/**
 * Request to list active channels.
 */
export const CentrifugoChannelsRequestRequestSchema = z.object({
  pattern: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoChannelsRequestRequest = z.infer<typeof CentrifugoChannelsRequestRequestSchema>
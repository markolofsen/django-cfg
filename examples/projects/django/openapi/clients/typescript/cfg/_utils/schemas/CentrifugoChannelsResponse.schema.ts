/**
 * Zod schema for CentrifugoChannelsResponse
 *
 * This schema provides runtime validation and type inference.
 *  * List of active channels response.
 *  */
import { z } from 'zod'
import { CentrifugoChannelsResultSchema } from './CentrifugoChannelsResult.schema'
import { CentrifugoErrorSchema } from './CentrifugoError.schema'

/**
 * List of active channels response.
 */
export const CentrifugoChannelsResponseSchema = z.object({
  error: CentrifugoErrorSchema.optional(),
  result: CentrifugoChannelsResultSchema.optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoChannelsResponse = z.infer<typeof CentrifugoChannelsResponseSchema>
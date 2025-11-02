/**
 * Zod schema for CentrifugoHistoryRequestRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Request to get channel history.
 *  */
import { z } from 'zod'
import { CentrifugoStreamPositionSchema } from './CentrifugoStreamPosition.schema'

/**
 * Request to get channel history.
 */
export const CentrifugoHistoryRequestRequestSchema = z.object({
  channel: z.string(),
  limit: z.string().nullable().optional(),
  since: CentrifugoStreamPositionSchema.optional(),
  reverse: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoHistoryRequestRequest = z.infer<typeof CentrifugoHistoryRequestRequestSchema>
/**
 * Zod schema for CentrifugoHistoryResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Channel history response.
 *  */
import { z } from 'zod'
import { CentrifugoErrorSchema } from './CentrifugoError.schema'
import { CentrifugoHistoryResultSchema } from './CentrifugoHistoryResult.schema'

/**
 * Channel history response.
 */
export const CentrifugoHistoryResponseSchema = z.object({
  error: CentrifugoErrorSchema.optional(),
  result: CentrifugoHistoryResultSchema.optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoHistoryResponse = z.infer<typeof CentrifugoHistoryResponseSchema>
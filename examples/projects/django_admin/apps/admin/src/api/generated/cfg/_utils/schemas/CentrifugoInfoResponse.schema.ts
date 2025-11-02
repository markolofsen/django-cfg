/**
 * Zod schema for CentrifugoInfoResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Server info response.
 *  */
import { z } from 'zod'
import { CentrifugoErrorSchema } from './CentrifugoError.schema'
import { CentrifugoInfoResultSchema } from './CentrifugoInfoResult.schema'

/**
 * Server info response.
 */
export const CentrifugoInfoResponseSchema = z.object({
  error: CentrifugoErrorSchema.optional(),
  result: CentrifugoInfoResultSchema.optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoInfoResponse = z.infer<typeof CentrifugoInfoResponseSchema>
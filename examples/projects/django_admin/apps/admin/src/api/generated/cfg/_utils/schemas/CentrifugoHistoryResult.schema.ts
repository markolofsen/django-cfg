/**
 * Zod schema for CentrifugoHistoryResult
 *
 * This schema provides runtime validation and type inference.
 *  * History result wrapper.
 *  */
import { z } from 'zod'
import { CentrifugoPublicationSchema } from './CentrifugoPublication.schema'

/**
 * History result wrapper.
 */
export const CentrifugoHistoryResultSchema = z.object({
  publications: z.array(CentrifugoPublicationSchema),
  epoch: z.string(),
  offset: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoHistoryResult = z.infer<typeof CentrifugoHistoryResultSchema>
/**
 * Zod schema for CentrifugoInfoResult
 *
 * This schema provides runtime validation and type inference.
 *  * Info result wrapper.
 *  */
import { z } from 'zod'
import { CentrifugoNodeInfoSchema } from './CentrifugoNodeInfo.schema'

/**
 * Info result wrapper.
 */
export const CentrifugoInfoResultSchema = z.object({
  nodes: z.array(CentrifugoNodeInfoSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoInfoResult = z.infer<typeof CentrifugoInfoResultSchema>
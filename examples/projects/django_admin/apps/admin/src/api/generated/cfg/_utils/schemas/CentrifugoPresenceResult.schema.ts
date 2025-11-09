/**
 * Zod schema for CentrifugoPresenceResult
 *
 * This schema provides runtime validation and type inference.
 *  * Presence result wrapper.
 *  */
import { z } from 'zod'
import { CentrifugoClientInfoSchema } from './CentrifugoClientInfo.schema'

/**
 * Presence result wrapper.
 */
export const CentrifugoPresenceResultSchema = z.object({
  presence: z.record(z.string(), CentrifugoClientInfoSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoPresenceResult = z.infer<typeof CentrifugoPresenceResultSchema>
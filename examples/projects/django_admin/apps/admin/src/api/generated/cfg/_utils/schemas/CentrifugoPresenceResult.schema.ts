/**
 * Zod schema for CentrifugoPresenceResult
 *
 * This schema provides runtime validation and type inference.
 *  * Presence result wrapper.
 *  */
import { z } from 'zod'

/**
 * Presence result wrapper.
 */
export const CentrifugoPresenceResultSchema = z.object({
  presence: z.record(z.string(), z.any()),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoPresenceResult = z.infer<typeof CentrifugoPresenceResultSchema>
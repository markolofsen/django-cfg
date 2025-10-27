/**
 * Zod schema for CentrifugoProcess
 *
 * This schema provides runtime validation and type inference.
 *  * Process information.
 *  */
import { z } from 'zod'

/**
 * Process information.
 */
export const CentrifugoProcessSchema = z.object({
  cpu: z.number(),
  rss: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoProcess = z.infer<typeof CentrifugoProcessSchema>
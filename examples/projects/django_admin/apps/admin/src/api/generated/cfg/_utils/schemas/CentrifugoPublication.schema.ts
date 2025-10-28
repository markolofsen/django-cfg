/**
 * Zod schema for CentrifugoPublication
 *
 * This schema provides runtime validation and type inference.
 *  * Single publication (message) in channel history.
 *  */
import { z } from 'zod'
import { CentrifugoClientInfoSchema } from './CentrifugoClientInfo.schema'

/**
 * Single publication (message) in channel history.
 */
export const CentrifugoPublicationSchema = z.object({
  data: z.record(z.string(), z.any()),
  info: CentrifugoClientInfoSchema.optional(),
  offset: z.int(),
  tags: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoPublication = z.infer<typeof CentrifugoPublicationSchema>
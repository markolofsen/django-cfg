/**
 * Zod schema for CentrifugoClientInfo
 *
 * This schema provides runtime validation and type inference.
 *  * Information about connected client.
 *  */
import { z } from 'zod'

/**
 * Information about connected client.
 */
export const CentrifugoClientInfoSchema = z.object({
  user: z.string(),
  client: z.string(),
  conn_info: z.string().nullable().optional(),
  chan_info: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CentrifugoClientInfo = z.infer<typeof CentrifugoClientInfoSchema>
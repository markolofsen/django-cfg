/**
 * Zod schema for ManualAckRequestRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Request model for manual ACK sending.
 *  */
import { z } from 'zod'

/**
 * Request model for manual ACK sending.
 */
export const ManualAckRequestRequestSchema = z.object({
  message_id: z.string(),
  client_id: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ManualAckRequestRequest = z.infer<typeof ManualAckRequestRequestSchema>
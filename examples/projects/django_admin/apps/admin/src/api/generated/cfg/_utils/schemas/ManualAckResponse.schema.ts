/**
 * Zod schema for ManualAckResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Response model for manual ACK.
 *  */
import { z } from 'zod'

/**
 * Response model for manual ACK.
 */
export const ManualAckResponseSchema = z.object({
  success: z.boolean(),
  message_id: z.string(),
  error: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ManualAckResponse = z.infer<typeof ManualAckResponseSchema>
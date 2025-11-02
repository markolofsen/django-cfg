/**
 * Zod schema for PublishTestResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Response model for test message publishing.
 *  */
import { z } from 'zod'

/**
 * Response model for test message publishing.
 */
export const PublishTestResponseSchema = z.object({
  success: z.boolean(),
  message_id: z.string(),
  channel: z.string(),
  acks_received: z.int().optional(),
  delivered: z.boolean().optional(),
  error: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PublishTestResponse = z.infer<typeof PublishTestResponseSchema>
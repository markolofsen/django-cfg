/**
 * Zod schema for PublishTestRequestRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Request model for test message publishing.
 *  */
import { z } from 'zod'

/**
 * Request model for test message publishing.
 */
export const PublishTestRequestRequestSchema = z.object({
  channel: z.string(),
  data: z.record(z.string(), z.any()),
  wait_for_ack: z.boolean().optional(),
  ack_timeout: z.int().min(1.0).max(60.0).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PublishTestRequestRequest = z.infer<typeof PublishTestRequestRequestSchema>
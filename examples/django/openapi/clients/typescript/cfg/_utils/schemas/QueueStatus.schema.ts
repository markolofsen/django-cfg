/**
 * Zod schema for QueueStatus
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for queue status data.
 *  */
import { z } from 'zod'

/**
 * Serializer for queue status data.
 */
export const QueueStatusSchema = z.object({
  queues: z.record(z.string(), z.any()),
  workers: z.number().int(),
  redis_connected: z.boolean(),
  timestamp: z.string(),
  error: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type QueueStatus = z.infer<typeof QueueStatusSchema>
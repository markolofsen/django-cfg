/**
 * Zod schema for QueueStats
 *
 * This schema provides runtime validation and type inference.
 *  * Queue statistics serializer.

Provides basic queue statistics.
 *  */
import { z } from 'zod'

/**
 * Queue statistics serializer.

Provides basic queue statistics.
 */
export const QueueStatsSchema = z.object({
  name: z.string(),
  count: z.int(),
  queued_jobs: z.int().optional(),
  started_jobs: z.int().optional(),
  finished_jobs: z.int().optional(),
  failed_jobs: z.int().optional(),
  deferred_jobs: z.int().optional(),
  scheduled_jobs: z.int().optional(),
  workers: z.int().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type QueueStats = z.infer<typeof QueueStatsSchema>
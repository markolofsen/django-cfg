/**
 * Zod schema for QueueDetail
 *
 * This schema provides runtime validation and type inference.
 *  * Detailed queue information serializer.

Provides comprehensive queue statistics and metadata.
 *  */
import { z } from 'zod'

/**
 * Detailed queue information serializer.

Provides comprehensive queue statistics and metadata.
 */
export const QueueDetailSchema = z.object({
  name: z.string(),
  count: z.int(),
  queued_jobs: z.int().optional(),
  started_jobs: z.int().optional(),
  finished_jobs: z.int().optional(),
  failed_jobs: z.int().optional(),
  deferred_jobs: z.int().optional(),
  scheduled_jobs: z.int().optional(),
  workers: z.int().optional(),
  oldest_job_timestamp: z.iso.datetime().nullable().optional(),
  connection_kwargs: z.record(z.string(), z.any()).optional(),
  is_async: z.boolean().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type QueueDetail = z.infer<typeof QueueDetailSchema>
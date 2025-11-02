/**
 * Zod schema for WorkerStats
 *
 * This schema provides runtime validation and type inference.
 *  * Aggregated worker statistics serializer.

Provides overview of all workers across all queues.
 *  */
import { z } from 'zod'
import { WorkerSchema } from './Worker.schema'

/**
 * Aggregated worker statistics serializer.

Provides overview of all workers across all queues.
 */
export const WorkerStatsSchema = z.object({
  total_workers: z.int(),
  busy_workers: z.int().optional(),
  idle_workers: z.int().optional(),
  suspended_workers: z.int().optional(),
  total_successful_jobs: z.int().optional(),
  total_failed_jobs: z.int().optional(),
  total_working_time: z.number().optional(),
  workers: z.array(WorkerSchema).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type WorkerStats = z.infer<typeof WorkerStatsSchema>
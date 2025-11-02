/**
 * Zod schema for Worker
 *
 * This schema provides runtime validation and type inference.
 *  * Worker information serializer.

Provides detailed information about an RQ worker.
 *  */
import { z } from 'zod'

/**
 * Worker information serializer.

Provides detailed information about an RQ worker.
 */
export const WorkerSchema = z.object({
  name: z.string(),
  queues: z.array(z.string()).optional(),
  state: z.string(),
  current_job: z.string().nullable().optional(),
  birth: z.iso.datetime(),
  last_heartbeat: z.iso.datetime(),
  successful_job_count: z.int().optional(),
  failed_job_count: z.int().optional(),
  total_working_time: z.number().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Worker = z.infer<typeof WorkerSchema>
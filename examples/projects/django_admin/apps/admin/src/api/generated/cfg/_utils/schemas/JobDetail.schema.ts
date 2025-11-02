/**
 * Zod schema for JobDetail
 *
 * This schema provides runtime validation and type inference.
 *  * Detailed job information serializer.

Provides comprehensive job details including result and metadata.
 *  */
import { z } from 'zod'

/**
 * Detailed job information serializer.

Provides comprehensive job details including result and metadata.
 */
export const JobDetailSchema = z.object({
  id: z.string(),
  func_name: z.string(),
  args: z.array(z.string()).optional(),
  kwargs: z.record(z.string(), z.any()).optional(),
  created_at: z.iso.datetime(),
  enqueued_at: z.iso.datetime().nullable().optional(),
  started_at: z.iso.datetime().nullable().optional(),
  ended_at: z.iso.datetime().nullable().optional(),
  status: z.string(),
  queue: z.string(),
  worker_name: z.string().nullable().optional(),
  timeout: z.int().nullable().optional(),
  result_ttl: z.int().nullable().optional(),
  failure_ttl: z.int().nullable().optional(),
  result: z.string().nullable().optional(),
  exc_info: z.string().nullable().optional(),
  meta: z.record(z.string(), z.any()).optional(),
  dependency_ids: z.array(z.string()).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type JobDetail = z.infer<typeof JobDetailSchema>
/**
 * Zod schema for ScheduledJob
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for scheduled job information.
 *  */
import { z } from 'zod'

/**
 * Serializer for scheduled job information.
 */
export const ScheduledJobSchema = z.object({
  id: z.string(),
  func: z.string(),
  args: z.array(z.record(z.string(), z.any())).optional(),
  kwargs: z.record(z.string(), z.any()).optional(),
  queue_name: z.string(),
  scheduled_time: z.iso.datetime().nullable().optional(),
  interval: z.int().nullable().optional(),
  cron: z.string().nullable().optional(),
  timeout: z.int().nullable().optional(),
  result_ttl: z.int().nullable().optional(),
  repeat: z.int().nullable().optional(),
  description: z.string().nullable().optional(),
  created_at: z.iso.datetime().nullable().optional(),
  meta: z.record(z.string(), z.any()).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ScheduledJob = z.infer<typeof ScheduledJobSchema>
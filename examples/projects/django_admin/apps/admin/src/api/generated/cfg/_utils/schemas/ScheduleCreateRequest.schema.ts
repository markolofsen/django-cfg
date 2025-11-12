/**
 * Zod schema for ScheduleCreateRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for creating a scheduled job.

Supports three scheduling methods:
1. scheduled_time: Schedule job at specific time
2. interval: Schedule job to repeat at intervals
3. cron: Schedule job with cron expression
 *  */
import { z } from 'zod'

/**
 * Serializer for creating a scheduled job.

Supports three scheduling methods:
1. scheduled_time: Schedule job at specific time
2. interval: Schedule job to repeat at intervals
3. cron: Schedule job with cron expression
 */
export const ScheduleCreateRequestSchema = z.object({
  func: z.string().min(1),
  args: z.array(z.record(z.string(), z.any())).optional(),
  kwargs: z.record(z.string(), z.any()).optional(),
  queue_name: z.string().min(1).optional(),
  scheduled_time: z.iso.datetime().nullable().optional(),
  interval: z.int().min(1.0).nullable().optional(),
  cron: z.string().min(1).nullable().optional(),
  timeout: z.int().nullable().optional(),
  result_ttl: z.int().nullable().optional(),
  repeat: z.int().nullable().optional(),
  description: z.string().min(1).max(255).nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ScheduleCreateRequest = z.infer<typeof ScheduleCreateRequestSchema>
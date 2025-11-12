/**
 * Zod schema for ScheduleInfo
 *
 * This schema provides runtime validation and type inference.
 *  * Schedule information in config response.
 *  */
import { z } from 'zod'

/**
 * Schedule information in config response.
 */
export const ScheduleInfoSchema = z.object({
  func: z.string(),
  queue: z.string(),
  cron: z.string().nullable().optional(),
  interval: z.int().nullable().optional(),
  scheduled_time: z.iso.datetime().nullable().optional(),
  description: z.string().nullable().optional(),
  timeout: z.int().nullable().optional(),
  result_ttl: z.int().nullable().optional(),
  repeat: z.int().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ScheduleInfo = z.infer<typeof ScheduleInfoSchema>
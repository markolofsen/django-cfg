/**
 * Zod schema for RQSchedule
 *
 * This schema provides runtime validation and type inference.
 *  * Redis Queue schedule configuration.
 *  */
import { z } from 'zod'

/**
 * Redis Queue schedule configuration.
 */
export const RQScheduleSchema = z.object({
  func: z.string().nullable().optional(),
  cron_string: z.string().nullable().optional(),
  queue: z.string().nullable().optional(),
  kwargs: z.record(z.string(), z.any()).nullable().optional(),
  args: z.array(z.record(z.string(), z.any())).nullable().optional(),
  meta: z.record(z.string(), z.any()).nullable().optional(),
  repeat: z.int().nullable().optional(),
  result_ttl: z.int().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type RQSchedule = z.infer<typeof RQScheduleSchema>
/**
 * Zod schema for TimelineItem
 *
 * This schema provides runtime validation and type inference.
 *  * Single timeline data point for DRF.
 *  */
import { z } from 'zod'

/**
 * Single timeline data point for DRF.
 */
export const TimelineItemSchema = z.object({
  timestamp: z.string(),
  count: z.int(),
  successful: z.int(),
  failed: z.int(),
  timeout: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type TimelineItem = z.infer<typeof TimelineItemSchema>
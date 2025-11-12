/**
 * Zod schema for TimelineResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Timeline response with hourly/daily breakdown for DRF.
 *  */
import { z } from 'zod'
import { TimelineItemSchema } from './TimelineItem.schema'

/**
 * Timeline response with hourly/daily breakdown for DRF.
 */
export const TimelineResponseSchema = z.object({
  timeline: z.array(TimelineItemSchema),
  period_hours: z.int(),
  interval: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type TimelineResponse = z.infer<typeof TimelineResponseSchema>
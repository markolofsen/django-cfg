/**
 * Zod schema for ActivityTrackerDay
 *
 * This schema provides runtime validation and type inference.
 *  * Activity tracker single day serializer.
 *  */
import { z } from 'zod'

/**
 * Activity tracker single day serializer.
 */
export const ActivityTrackerDaySchema = z.object({
  date: z.iso.date(),
  count: z.int(),
  level: z.int(),
  color: z.string(),
  tooltip: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ActivityTrackerDay = z.infer<typeof ActivityTrackerDaySchema>
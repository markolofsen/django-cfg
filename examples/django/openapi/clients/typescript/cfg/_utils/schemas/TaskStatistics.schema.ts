/**
 * Zod schema for TaskStatistics
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for task statistics data.
 *  */
import { z } from 'zod'

/**
 * Serializer for task statistics data.
 */
export const TaskStatisticsSchema = z.object({
  statistics: z.record(z.string(), z.any()),
  recent_tasks: z.array(z.record(z.string(), z.any())),
  timestamp: z.string(),
  error: z.string().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type TaskStatistics = z.infer<typeof TaskStatisticsSchema>
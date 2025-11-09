/**
 * Zod schema for ServerLifecycleChart
 *
 * This schema provides runtime validation and type inference.
 *  * Server lifecycle events timeline.
 *  */
import { z } from 'zod'
import { ServerLifecycleEventSchema } from './ServerLifecycleEvent.schema'

/**
 * Server lifecycle events timeline.
 */
export const ServerLifecycleChartSchema = z.object({
  title: z.string().optional(),
  events: z.array(ServerLifecycleEventSchema).optional(),
  period_hours: z.int(),
  total_events: z.int(),
  restart_count: z.int(),
  error_count: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ServerLifecycleChart = z.infer<typeof ServerLifecycleChartSchema>
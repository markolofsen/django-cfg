/**
 * Zod schema for ServerUptimeChart
 *
 * This schema provides runtime validation and type inference.
 *  * Server uptime over time chart data.
 *  */
import { z } from 'zod'
import { ServerUptimeDataPointSchema } from './ServerUptimeDataPoint.schema'

/**
 * Server uptime over time chart data.
 */
export const ServerUptimeChartSchema = z.object({
  title: z.string().optional(),
  data_points: z.array(ServerUptimeDataPointSchema).optional(),
  period_hours: z.int(),
  granularity: z.string(),
  total_servers: z.int(),
  currently_running: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ServerUptimeChart = z.infer<typeof ServerUptimeChartSchema>
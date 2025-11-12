/**
 * Zod schema for DashboardCharts
 *
 * This schema provides runtime validation and type inference.
 *  * Combined dashboard charts data.
 *  */
import { z } from 'zod'
import { ErrorDistributionChartSchema } from './ErrorDistributionChart.schema'
import { RequestVolumeChartSchema } from './RequestVolumeChart.schema'
import { ResponseTimeChartSchema } from './ResponseTimeChart.schema'
import { ServerUptimeChartSchema } from './ServerUptimeChart.schema'
import { ServiceActivityChartSchema } from './ServiceActivityChart.schema'

/**
 * Combined dashboard charts data.
 */
export const DashboardChartsSchema = z.object({
  server_uptime: ServerUptimeChartSchema,
  request_volume: RequestVolumeChartSchema,
  response_time: ResponseTimeChartSchema,
  service_activity: ServiceActivityChartSchema,
  error_distribution: ErrorDistributionChartSchema,
  period_hours: z.int(),
  generated_at: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type DashboardCharts = z.infer<typeof DashboardChartsSchema>
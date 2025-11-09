/**
 * Zod schema for ResponseTimeChart
 *
 * This schema provides runtime validation and type inference.
 *  * Response time over time chart data.
 *  */
import { z } from 'zod'
import { ResponseTimeDataPointSchema } from './ResponseTimeDataPoint.schema'

/**
 * Response time over time chart data.
 */
export const ResponseTimeChartSchema = z.object({
  title: z.string().optional(),
  data_points: z.array(ResponseTimeDataPointSchema).optional(),
  period_hours: z.int(),
  granularity: z.string(),
  overall_avg_ms: z.number(),
  overall_p95_ms: z.number(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ResponseTimeChart = z.infer<typeof ResponseTimeChartSchema>
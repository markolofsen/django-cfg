/**
 * Zod schema for RequestVolumeChart
 *
 * This schema provides runtime validation and type inference.
 *  * Request volume over time chart data.
 *  */
import { z } from 'zod'
import { RequestVolumeDataPointSchema } from './RequestVolumeDataPoint.schema'

/**
 * Request volume over time chart data.
 */
export const RequestVolumeChartSchema = z.object({
  title: z.string().optional(),
  data_points: z.array(RequestVolumeDataPointSchema).optional(),
  period_hours: z.int(),
  granularity: z.string(),
  total_requests: z.int(),
  avg_success_rate: z.number(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type RequestVolumeChart = z.infer<typeof RequestVolumeChartSchema>
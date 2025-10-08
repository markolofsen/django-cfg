/**
 * Zod schema for ChartSeries
 *
 * This schema provides runtime validation and type inference.
 *  * Chart series data for payments visualization
 *  */
import { z } from 'zod'
import { ChartDataPointSchema } from './ChartDataPoint.schema'

/**
 * Chart series data for payments visualization
 */
export const ChartSeriesSchema = z.object({
  name: z.string(),
  data: z.array(ChartDataPointSchema),
  color: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ChartSeries = z.infer<typeof ChartSeriesSchema>
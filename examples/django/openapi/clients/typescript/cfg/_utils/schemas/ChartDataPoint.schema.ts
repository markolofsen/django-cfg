/**
 * Zod schema for ChartDataPoint
 *
 * This schema provides runtime validation and type inference.
 *  * Chart data point for payments analytics
 *  */
import { z } from 'zod'

/**
 * Chart data point for payments analytics
 */
export const ChartDataPointSchema = z.object({
  x: z.string(),
  y: z.number(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ChartDataPoint = z.infer<typeof ChartDataPointSchema>
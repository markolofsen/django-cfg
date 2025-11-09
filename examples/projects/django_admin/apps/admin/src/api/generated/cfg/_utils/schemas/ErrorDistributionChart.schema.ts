/**
 * Zod schema for ErrorDistributionChart
 *
 * This schema provides runtime validation and type inference.
 *  * Error distribution chart data.
 *  */
import { z } from 'zod'
import { ErrorDistributionDataPointSchema } from './ErrorDistributionDataPoint.schema'

/**
 * Error distribution chart data.
 */
export const ErrorDistributionChartSchema = z.object({
  title: z.string().optional(),
  error_types: z.array(ErrorDistributionDataPointSchema).optional(),
  period_hours: z.int(),
  total_errors: z.int(),
  most_common_error: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ErrorDistributionChart = z.infer<typeof ErrorDistributionChartSchema>
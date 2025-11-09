/**
 * Zod schema for ErrorDistributionDataPoint
 *
 * This schema provides runtime validation and type inference.
 *  * Error distribution data point.
 *  */
import { z } from 'zod'

/**
 * Error distribution data point.
 */
export const ErrorDistributionDataPointSchema = z.object({
  error_code: z.string(),
  count: z.int(),
  percentage: z.number(),
  service_name: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ErrorDistributionDataPoint = z.infer<typeof ErrorDistributionDataPointSchema>
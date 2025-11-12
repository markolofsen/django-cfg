/**
 * Zod schema for RequestVolumeDataPoint
 *
 * This schema provides runtime validation and type inference.
 *  * Request volume data point.
 *  */
import { z } from 'zod'

/**
 * Request volume data point.
 */
export const RequestVolumeDataPointSchema = z.object({
  timestamp: z.string(),
  total_requests: z.int(),
  successful_requests: z.int(),
  failed_requests: z.int(),
  success_rate: z.number(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type RequestVolumeDataPoint = z.infer<typeof RequestVolumeDataPointSchema>
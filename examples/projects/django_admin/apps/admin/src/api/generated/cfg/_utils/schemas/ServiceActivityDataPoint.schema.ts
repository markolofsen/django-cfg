/**
 * Zod schema for ServiceActivityDataPoint
 *
 * This schema provides runtime validation and type inference.
 *  * Service activity data point.
 *  */
import { z } from 'zod'

/**
 * Service activity data point.
 */
export const ServiceActivityDataPointSchema = z.object({
  service_name: z.string(),
  request_count: z.int(),
  success_rate: z.number(),
  avg_duration_ms: z.number(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ServiceActivityDataPoint = z.infer<typeof ServiceActivityDataPointSchema>
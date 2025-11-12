/**
 * Zod schema for ResponseTimeDataPoint
 *
 * This schema provides runtime validation and type inference.
 *  * Response time statistics data point.
 *  */
import { z } from 'zod'

/**
 * Response time statistics data point.
 */
export const ResponseTimeDataPointSchema = z.object({
  timestamp: z.string(),
  avg_duration_ms: z.number(),
  p50_duration_ms: z.number(),
  p95_duration_ms: z.number(),
  p99_duration_ms: z.number(),
  min_duration_ms: z.number(),
  max_duration_ms: z.number(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ResponseTimeDataPoint = z.infer<typeof ResponseTimeDataPointSchema>
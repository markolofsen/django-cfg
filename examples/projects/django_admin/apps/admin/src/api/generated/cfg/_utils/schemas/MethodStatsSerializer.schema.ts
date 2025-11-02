/**
 * Zod schema for MethodStatsSerializer
 *
 * This schema provides runtime validation and type inference.
 *  * Statistics for a single gRPC method.
 *  */
import { z } from 'zod'

/**
 * Statistics for a single gRPC method.
 */
export const MethodStatsSerializerSchema = z.object({
  method_name: z.string(),
  service_name: z.string(),
  total: z.int(),
  successful: z.int(),
  errors: z.int(),
  avg_duration_ms: z.number(),
  last_activity_at: z.string().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type MethodStatsSerializer = z.infer<typeof MethodStatsSerializerSchema>
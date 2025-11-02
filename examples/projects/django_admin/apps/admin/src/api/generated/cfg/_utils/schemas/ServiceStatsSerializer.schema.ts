/**
 * Zod schema for ServiceStatsSerializer
 *
 * This schema provides runtime validation and type inference.
 *  * Statistics for a single gRPC service.
 *  */
import { z } from 'zod'

/**
 * Statistics for a single gRPC service.
 */
export const ServiceStatsSerializerSchema = z.object({
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
export type ServiceStatsSerializer = z.infer<typeof ServiceStatsSerializerSchema>
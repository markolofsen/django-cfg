/**
 * Zod schema for ServiceStats
 *
 * This schema provides runtime validation and type inference.
 *  * Service statistics.
 *  */
import { z } from 'zod'

/**
 * Service statistics.
 */
export const ServiceStatsSchema = z.object({
  total_requests: z.int().optional(),
  successful: z.int().optional(),
  errors: z.int().optional(),
  success_rate: z.number().optional(),
  avg_duration_ms: z.number().optional(),
  last_24h_requests: z.int().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ServiceStats = z.infer<typeof ServiceStatsSchema>
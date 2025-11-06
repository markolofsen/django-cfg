/**
 * Zod schema for GRPCStats
 *
 * This schema provides runtime validation and type inference.
 *  * Runtime statistics summary.
 *  */
import { z } from 'zod'

/**
 * Runtime statistics summary.
 */
export const GRPCStatsSchema = z.object({
  total_requests: z.int(),
  success_rate: z.number(),
  avg_duration_ms: z.number(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type GRPCStats = z.infer<typeof GRPCStatsSchema>
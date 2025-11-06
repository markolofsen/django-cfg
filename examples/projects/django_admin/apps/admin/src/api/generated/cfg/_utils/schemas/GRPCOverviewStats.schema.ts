/**
 * Zod schema for GRPCOverviewStats
 *
 * This schema provides runtime validation and type inference.
 *  * Overview statistics for gRPC requests.
 *  */
import { z } from 'zod'
import { GRPCServerStatusSchema } from './GRPCServerStatus.schema'

/**
 * Overview statistics for gRPC requests.
 */
export const GRPCOverviewStatsSchema = z.object({
  total: z.int(),
  successful: z.int(),
  errors: z.int(),
  cancelled: z.int(),
  timeout: z.int(),
  success_rate: z.number(),
  avg_duration_ms: z.number(),
  p95_duration_ms: z.number().nullable(),
  period_hours: z.int(),
  server: GRPCServerStatusSchema,
})

/**
 * Infer TypeScript type from Zod schema
 */
export type GRPCOverviewStats = z.infer<typeof GRPCOverviewStatsSchema>
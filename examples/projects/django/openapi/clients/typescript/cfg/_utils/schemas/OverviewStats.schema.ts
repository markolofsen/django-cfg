/**
 * Zod schema for OverviewStats
 *
 * This schema provides runtime validation and type inference.
 *  * Overview statistics for Centrifugo publishes.
 *  */
import { z } from 'zod'

/**
 * Overview statistics for Centrifugo publishes.
 */
export const OverviewStatsSchema = z.object({
  total: z.int(),
  successful: z.int(),
  failed: z.int(),
  timeout: z.int(),
  success_rate: z.number(),
  avg_duration_ms: z.number(),
  avg_acks_received: z.number(),
  period_hours: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type OverviewStats = z.infer<typeof OverviewStatsSchema>
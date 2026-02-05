/**
 * Zod schema for PortfolioStats
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for portfolio statistics.
 *  */
import { z } from 'zod';

/**
 * Serializer for portfolio statistics.
 */
export const PortfolioStatsSchema = z.object({
  total_portfolios: z.int(),
  total_volume_usd: z.string(),
  total_orders: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PortfolioStats = z.infer<typeof PortfolioStatsSchema>
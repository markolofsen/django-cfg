/**
 * Zod schema for CoinStats
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for coin statistics.
 *  */
import { z } from 'zod'
import { CoinListSchema } from './CoinList.schema'

/**
 * Serializer for coin statistics.
 */
export const CoinStatsSchema = z.object({
  total_coins: z.int(),
  total_market_cap_usd: z.string(),
  total_volume_24h_usd: z.string(),
  trending_coins: z.array(CoinListSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CoinStats = z.infer<typeof CoinStatsSchema>
/**
 * Zod schema for CoinList
 *
 * This schema provides runtime validation and type inference.
 *  * Lightweight serializer for coin lists.
 *  */
import { z } from 'zod';

/**
 * Lightweight serializer for coin lists.
 */
export const CoinListSchema = z.object({
  id: z.int(),
  symbol: z.string().max(10),
  name: z.string().max(100),
  slug: z.string().max(100),
  current_price_usd: z.string().optional(),
  market_cap_usd: z.string().optional(),
  price_change_24h_percent: z.string().optional(),
  logo_url: z.url().optional(),
  rank: z.int().min(0.0).max(2147483647.0).optional(),
  is_price_up_24h: z.boolean(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CoinList = z.infer<typeof CoinListSchema>
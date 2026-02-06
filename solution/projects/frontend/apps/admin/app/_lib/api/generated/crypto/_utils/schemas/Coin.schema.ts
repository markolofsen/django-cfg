/**
 * Zod schema for Coin
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for coins.
 *  */
import { z } from 'zod'

/**
 * Serializer for coins.
 */
export const CoinSchema = z.object({
  id: z.int(),
  symbol: z.string().max(10),
  name: z.string().max(100),
  slug: z.string().max(100),
  current_price_usd: z.string().optional(),
  market_cap_usd: z.string().optional(),
  volume_24h_usd: z.string().optional(),
  price_change_24h_percent: z.string().optional(),
  price_change_7d_percent: z.string().optional(),
  price_change_30d_percent: z.string().optional(),
  logo_url: z.union([z.url(), z.literal('')]).optional(),
  description: z.string().optional(),
  website: z.union([z.url(), z.literal('')]).optional(),
  whitepaper_url: z.union([z.url(), z.literal('')]).optional(),
  rank: z.int().min(0.0).max(2147483647.0).optional(),
  is_active: z.boolean().optional(),
  is_tradeable: z.boolean().optional(),
  is_price_up_24h: z.boolean(),
  created_at: z.string().datetime({ offset: true }),
  updated_at: z.string().datetime({ offset: true }),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Coin = z.infer<typeof CoinSchema>
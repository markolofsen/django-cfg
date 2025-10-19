/**
 * Zod schema for Exchange
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for exchanges.
 *  */
import { z } from 'zod'

/**
 * Serializer for exchanges.
 */
export const ExchangeSchema = z.object({
  id: z.int(),
  name: z.string().max(100),
  slug: z.string().max(100),
  code: z.string().max(20),
  description: z.string().optional(),
  website: z.url().optional(),
  logo_url: z.url().optional(),
  volume_24h_usd: z.string().optional(),
  num_markets: z.int().min(0.0).max(2147483647.0).optional(),
  num_coins: z.int().min(0.0).max(2147483647.0).optional(),
  maker_fee_percent: z.string().optional(),
  taker_fee_percent: z.string().optional(),
  is_active: z.boolean().optional(),
  is_verified: z.boolean().optional(),
  supports_api: z.boolean().optional(),
  rank: z.int().min(0.0).max(2147483647.0).optional(),
  created_at: z.iso.datetime(),
  updated_at: z.iso.datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Exchange = z.infer<typeof ExchangeSchema>
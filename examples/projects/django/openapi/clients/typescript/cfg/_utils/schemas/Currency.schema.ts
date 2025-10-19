/**
 * Zod schema for Currency
 *
 * This schema provides runtime validation and type inference.
 *  * Currency list serializer.
 *  */
import { z } from 'zod'

/**
 * Currency list serializer.
 */
export const CurrencySchema = z.object({
  code: z.string(),
  name: z.string(),
  token: z.string(),
  network: z.string().nullable(),
  display_name: z.string(),
  symbol: z.string(),
  decimal_places: z.int(),
  is_active: z.boolean(),
  min_amount_usd: z.string(),
  sort_order: z.int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Currency = z.infer<typeof CurrencySchema>
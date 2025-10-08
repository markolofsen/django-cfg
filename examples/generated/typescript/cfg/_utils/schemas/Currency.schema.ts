/**
 * Zod schema for Currency
 *
 * This schema provides runtime validation and type inference.
 *  * Complete currency serializer with full details.

Used for currency information and management.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Complete currency serializer with full details.

Used for currency information and management.
 */
export const CurrencySchema = z.object({
  id: z.number().int(),
  code: z.string(),
  name: z.string(),
  symbol: z.string(),
  currency_type: z.nativeEnum(Enums.CurrencyCurrencyType),
  type_display: z.string(),
  decimal_places: z.number().int(),
  is_active: z.boolean(),
  is_crypto: z.boolean(),
  is_fiat: z.boolean(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Currency = z.infer<typeof CurrencySchema>
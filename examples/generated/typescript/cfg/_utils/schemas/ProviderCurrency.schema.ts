/**
 * Zod schema for ProviderCurrency
 *
 * This schema provides runtime validation and type inference.
 *  * Provider currency serializer for provider-specific currency info.

Used for provider currency management and rates.
 *  */
import { z } from 'zod'
import { CurrencyListSchema } from './CurrencyList.schema'
import { NetworkSchema } from './Network.schema'

/**
 * Provider currency serializer for provider-specific currency info.

Used for provider currency management and rates.
 */
export const ProviderCurrencySchema = z.object({
  id: z.number().int(),
  currency: CurrencyListSchema,
  network: NetworkSchema,
  provider: z.string(),
  provider_currency_code: z.string(),
  provider_min_amount_usd: z.number(),
  provider_max_amount_usd: z.number(),
  provider_fee_percentage: z.number(),
  provider_fixed_fee_usd: z.number(),
  is_enabled: z.boolean(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ProviderCurrency = z.infer<typeof ProviderCurrencySchema>
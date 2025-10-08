/**
 * Zod schema for CurrencyList
 *
 * This schema provides runtime validation and type inference.
 *  * Lightweight currency serializer for lists.

Optimized for currency selection and lists.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Lightweight currency serializer for lists.

Optimized for currency selection and lists.
 */
export const CurrencyListSchema = z.object({
  id: z.number().int(),
  code: z.string(),
  name: z.string(),
  symbol: z.string(),
  currency_type: z.nativeEnum(Enums.CurrencyListCurrencyType),
  type_display: z.string(),
  is_active: z.boolean(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CurrencyList = z.infer<typeof CurrencyListSchema>
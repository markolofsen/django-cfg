/**
 * Zod schema for CurrencyAnalyticsItem
 *
 * This schema provides runtime validation and type inference.
 *  * Analytics data for a single currency
 *  */
import { z } from 'zod'

/**
 * Analytics data for a single currency
 */
export const CurrencyAnalyticsItemSchema = z.object({
  currency_code: z.string(),
  currency_name: z.string(),
  total_payments: z.number().int(),
  total_amount: z.number(),
  completed_payments: z.number().int(),
  average_amount: z.number(),
  success_rate: z.number(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type CurrencyAnalyticsItem = z.infer<typeof CurrencyAnalyticsItemSchema>
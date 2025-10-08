/**
 * Zod schema for PaymentAnalyticsResponse
 *
 * This schema provides runtime validation and type inference.
 *  * Payment analytics response with currency and provider breakdown
 *  */
import { z } from 'zod'
import { CurrencyAnalyticsItemSchema } from './CurrencyAnalyticsItem.schema'
import { ProviderAnalyticsItemSchema } from './ProviderAnalyticsItem.schema'

/**
 * Payment analytics response with currency and provider breakdown
 */
export const PaymentAnalyticsResponseSchema = z.object({
  currency_analytics: z.array(CurrencyAnalyticsItemSchema),
  provider_analytics: z.array(ProviderAnalyticsItemSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaymentAnalyticsResponse = z.infer<typeof PaymentAnalyticsResponseSchema>
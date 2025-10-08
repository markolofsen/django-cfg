/**
 * Zod schema for ProviderAnalyticsItem
 *
 * This schema provides runtime validation and type inference.
 *  * Analytics data for a single payment provider
 *  */
import { z } from 'zod'

/**
 * Analytics data for a single payment provider
 */
export const ProviderAnalyticsItemSchema = z.object({
  provider: z.string(),
  provider_display: z.string(),
  total_payments: z.number().int(),
  total_amount: z.number(),
  completed_payments: z.number().int(),
  success_rate: z.number(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ProviderAnalyticsItem = z.infer<typeof ProviderAnalyticsItemSchema>
/**
 * Zod schema for AdminPaymentStats
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for payment statistics in admin interface.
 *  */
import { z } from 'zod'

/**
 * Serializer for payment statistics in admin interface.
 */
export const AdminPaymentStatsSchema = z.object({
  total_payments: z.number().int(),
  total_amount_usd: z.number(),
  successful_payments: z.number().int(),
  failed_payments: z.number().int(),
  pending_payments: z.number().int(),
  success_rate: z.number(),
  by_provider: z.record(z.string(), z.any()),
  by_currency: z.record(z.string(), z.any()),
  last_24h: z.record(z.string(), z.any()),
  last_7d: z.record(z.string(), z.any()),
  last_30d: z.record(z.string(), z.any()),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type AdminPaymentStats = z.infer<typeof AdminPaymentStatsSchema>
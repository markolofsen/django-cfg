/**
 * Zod schema for PaymentsNowPayments
 *
 * This schema provides runtime validation and type inference.
 *  * NowPayments configuration.
 *  */
import { z } from 'zod'

/**
 * NowPayments configuration.
 */
export const PaymentsNowPaymentsSchema = z.object({
  api_key: z.string().nullable().optional(),
  ipn_secret: z.string().nullable().optional(),
  sandbox: z.boolean().nullable().optional(),
  enabled: z.boolean().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaymentsNowPayments = z.infer<typeof PaymentsNowPaymentsSchema>
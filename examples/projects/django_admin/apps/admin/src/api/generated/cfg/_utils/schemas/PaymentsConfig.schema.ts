/**
 * Zod schema for PaymentsConfig
 *
 * This schema provides runtime validation and type inference.
 *  * Payments configuration.
 *  */
import { z } from 'zod'
import { PaymentsNowPaymentsSchema } from './PaymentsNowPayments.schema'

/**
 * Payments configuration.
 */
export const PaymentsConfigSchema = z.object({
  enabled: z.boolean().nullable().optional(),
  nowpayments: PaymentsNowPaymentsSchema.nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaymentsConfig = z.infer<typeof PaymentsConfigSchema>
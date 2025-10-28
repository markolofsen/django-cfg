/**
 * Zod schema for PaymentDetail
 *
 * This schema provides runtime validation and type inference.
 *  * Detailed payment information.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Detailed payment information.
 */
export const PaymentDetailSchema = z.object({
  id: z.uuid(),
  internal_payment_id: z.string(),
  amount_usd: z.string(),
  currency_code: z.string(),
  currency_name: z.string(),
  currency_token: z.string(),
  currency_network: z.string(),
  pay_amount: z.string().nullable(),
  actual_amount: z.string().nullable(),
  actual_amount_usd: z.string().nullable(),
  status: z.nativeEnum(Enums.PaymentDetailStatus),
  status_display: z.string(),
  pay_address: z.string().nullable(),
  qr_code_url: z.string().nullable(),
  payment_url: z.url().nullable(),
  transaction_hash: z.string().nullable(),
  explorer_link: z.string().nullable(),
  confirmations_count: z.int(),
  expires_at: z.iso.datetime().nullable(),
  completed_at: z.iso.datetime().nullable(),
  created_at: z.iso.datetime(),
  is_completed: z.boolean(),
  is_failed: z.boolean(),
  is_expired: z.boolean(),
  description: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaymentDetail = z.infer<typeof PaymentDetailSchema>
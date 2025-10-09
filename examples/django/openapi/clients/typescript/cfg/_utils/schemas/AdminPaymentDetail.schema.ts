/**
 * Zod schema for AdminPaymentDetail
 *
 * This schema provides runtime validation and type inference.
 *  * Detailed serializer for individual payment in admin interface.
Uses UniversalPayment only for data extraction.
 *  */
import { z } from 'zod'
import { AdminUserSchema } from './AdminUser.schema'

/**
 * Detailed serializer for individual payment in admin interface.
Uses UniversalPayment only for data extraction.
 */
export const AdminPaymentDetailSchema = z.object({
  id: z.string().uuid(),
  user: AdminUserSchema,
  internal_payment_id: z.string(),
  amount_usd: z.number(),
  actual_amount_usd: z.number(),
  fee_amount_usd: z.number(),
  currency_code: z.string(),
  currency_name: z.string(),
  provider: z.string(),
  provider_display: z.string(),
  status: z.string(),
  status_display: z.string(),
  pay_amount: z.string().regex(/^-?\\d{0,12}(?:\\.\\d{0,8})?$/),
  pay_address: z.string(),
  payment_url: z.string().url(),
  transaction_hash: z.string(),
  confirmations_count: z.number().int(),
  security_nonce: z.string(),
  expires_at: z.string().datetime(),
  completed_at: z.string().datetime(),
  status_changed_at: z.string().datetime(),
  description: z.string(),
  callback_url: z.string().url(),
  cancel_url: z.string().url(),
  provider_data: z.string(),
  webhook_data: z.string(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  age: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type AdminPaymentDetail = z.infer<typeof AdminPaymentDetailSchema>
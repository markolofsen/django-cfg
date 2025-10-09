/**
 * Zod schema for AdminPaymentList
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for payment list in admin interface.
Uses UniversalPayment only for data extraction.
 *  */
import { z } from 'zod'
import { AdminUserSchema } from './AdminUser.schema'

/**
 * Serializer for payment list in admin interface.
Uses UniversalPayment only for data extraction.
 */
export const AdminPaymentListSchema = z.object({
  id: z.string().uuid(),
  user: AdminUserSchema,
  amount_usd: z.number(),
  currency_code: z.string(),
  currency_name: z.string(),
  provider: z.string(),
  provider_display: z.string(),
  status: z.string(),
  status_display: z.string(),
  pay_amount: z.string().regex(/^-?\\d{0,12}(?:\\.\\d{0,8})?$/),
  pay_address: z.string(),
  transaction_hash: z.string(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  description: z.string(),
  age: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type AdminPaymentList = z.infer<typeof AdminPaymentListSchema>
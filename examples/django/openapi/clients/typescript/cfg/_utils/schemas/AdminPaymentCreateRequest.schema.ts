/**
 * Zod schema for AdminPaymentCreateRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for creating payments in admin interface.
Uses UniversalPayment only for data creation.
 *  */
import { z } from 'zod'

/**
 * Serializer for creating payments in admin interface.
Uses UniversalPayment only for data creation.
 */
export const AdminPaymentCreateRequestSchema = z.object({
  user: z.number().int(),
  amount_usd: z.number().min(1.0).max(100000.0),
  currency_code: z.string().min(1).max(20),
  provider: z.string().min(1).max(50),
  description: z.string().optional(),
  callback_url: z.string().url().optional(),
  cancel_url: z.string().url().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type AdminPaymentCreateRequest = z.infer<typeof AdminPaymentCreateRequestSchema>
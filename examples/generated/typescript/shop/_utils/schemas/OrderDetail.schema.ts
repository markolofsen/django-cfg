/**
 * Zod schema for OrderDetail
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for order detail view.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'
import { OrderItemSchema } from './OrderItem.schema'

/**
 * Serializer for order detail view.
 */
export const OrderDetailSchema = z.object({
  id: z.number().int(),
  order_number: z.string().max(50),
  customer: z.string(),
  status: z.nativeEnum(Enums.OrderDetailStatus).optional(),
  subtotal: z.string().regex(/^-?\\d{0,8}(?:\\.\\d{0,2})?$/).optional(),
  tax_amount: z.string().regex(/^-?\\d{0,8}(?:\\.\\d{0,2})?$/).optional(),
  shipping_amount: z.string().regex(/^-?\\d{0,8}(?:\\.\\d{0,2})?$/).optional(),
  discount_amount: z.string().regex(/^-?\\d{0,8}(?:\\.\\d{0,2})?$/).optional(),
  total_amount: z.string().regex(/^-?\\d{0,8}(?:\\.\\d{0,2})?$/).optional(),
  billing_address: z.string(),
  shipping_address: z.string(),
  customer_notes: z.string().optional(),
  admin_notes: z.string().optional(),
  items: z.array(OrderItemSchema),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  shipped_at: z.string().datetime().optional().nullable(),
  delivered_at: z.string().datetime().optional().nullable(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type OrderDetail = z.infer<typeof OrderDetailSchema>
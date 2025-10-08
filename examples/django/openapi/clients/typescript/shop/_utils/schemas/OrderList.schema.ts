/**
 * Zod schema for OrderList
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for order list view.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for order list view.
 */
export const OrderListSchema = z.object({
  id: z.number().int(),
  order_number: z.string().max(50),
  customer: z.string(),
  status: z.nativeEnum(Enums.OrderListStatus).optional(),
  subtotal: z.string().regex(/^-?\\d{0,8}(?:\\.\\d{0,2})?$/).optional(),
  total_amount: z.string().regex(/^-?\\d{0,8}(?:\\.\\d{0,2})?$/).optional(),
  items_count: z.number().int(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type OrderList = z.infer<typeof OrderListSchema>
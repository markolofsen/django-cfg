/**
 * Zod schema for Order
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for orders.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for orders.
 */
export const OrderSchema = z.object({
  id: z.int(),
  portfolio: z.int(),
  symbol: z.string().max(20),
  order_type: z.nativeEnum(Enums.OrderOrderType).optional(),
  side: z.nativeEnum(Enums.OrderSide),
  quantity: z.string(),
  price: z.string().nullable().optional(),
  filled_quantity: z.string(),
  status: z.nativeEnum(Enums.OrderStatus),
  total_usd: z.string(),
  created_at: z.iso.datetime(),
  updated_at: z.iso.datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Order = z.infer<typeof OrderSchema>
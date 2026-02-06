/**
 * Zod schema for OrderRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for orders.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for orders.
 */
export const OrderRequestSchema = z.object({
  portfolio: z.int(),
  symbol: z.string().min(1).max(20),
  order_type: z.nativeEnum(Enums.OrderOrderType).optional(),
  side: z.nativeEnum(Enums.OrderSide),
  quantity: z.string(),
  price: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type OrderRequest = z.infer<typeof OrderRequestSchema>
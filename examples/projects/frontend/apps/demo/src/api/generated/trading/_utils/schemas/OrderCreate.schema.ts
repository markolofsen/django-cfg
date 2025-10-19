/**
 * Zod schema for OrderCreate
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for creating orders.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for creating orders.
 */
export const OrderCreateSchema = z.object({
  symbol: z.string().max(20),
  order_type: z.nativeEnum(Enums.OrderCreateOrderType).optional(),
  side: z.nativeEnum(Enums.OrderCreateSide),
  quantity: z.string(),
  price: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type OrderCreate = z.infer<typeof OrderCreateSchema>
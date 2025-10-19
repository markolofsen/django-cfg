/**
 * Zod schema for PatchedOrderRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for orders.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Serializer for orders.
 */
export const PatchedOrderRequestSchema = z.object({
  portfolio: z.int().optional(),
  symbol: z.string().min(1).max(20).optional(),
  order_type: z.nativeEnum(Enums.PatchedOrderRequestOrderType).optional(),
  side: z.nativeEnum(Enums.PatchedOrderRequestSide).optional(),
  quantity: z.string().optional(),
  price: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedOrderRequest = z.infer<typeof PatchedOrderRequestSchema>
/**
 * Zod schema for OrderCreateRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for creating orders.
 *  */
import { z } from 'zod';

import * as Enums from '../../enums';

/**
 * Serializer for creating orders.
 */
export const OrderCreateRequestSchema = z.object({
  symbol: z.string().min(1).max(20),
  order_type: z.nativeEnum(Enums.OrderCreateRequestOrderType).optional(),
  side: z.nativeEnum(Enums.OrderCreateRequestSide),
  quantity: z.string(),
  price: z.string().nullable().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type OrderCreateRequest = z.infer<typeof OrderCreateRequestSchema>
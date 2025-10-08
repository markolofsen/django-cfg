/**
 * Zod schema for ShopStats
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for shop statistics.
 *  */
import { z } from 'zod'
import { OrderListSchema } from './OrderList.schema'
import { ProductListSchema } from './ProductList.schema'

/**
 * Serializer for shop statistics.
 */
export const ShopStatsSchema = z.object({
  total_products: z.number().int(),
  active_products: z.number().int(),
  out_of_stock_products: z.number().int(),
  total_orders: z.number().int(),
  pending_orders: z.number().int(),
  total_revenue: z.string().regex(/^-?\\d{0,10}(?:\\.\\d{0,2})?$/),
  popular_products: z.array(ProductListSchema),
  recent_orders: z.array(OrderListSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ShopStats = z.infer<typeof ShopStatsSchema>
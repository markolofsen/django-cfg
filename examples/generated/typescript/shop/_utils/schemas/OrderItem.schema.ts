/**
 * Zod schema for OrderItem
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for order items.
 *  */
import { z } from 'zod'
import { ProductListSchema } from './ProductList.schema'

/**
 * Serializer for order items.
 */
export const OrderItemSchema = z.object({
  id: z.number().int(),
  product: ProductListSchema,
  quantity: z.number().int().min(0.0).max(9.223372036854776e+18).optional(),
  unit_price: z.string().regex(/^-?\\d{0,8}(?:\\.\\d{0,2})?$/),
  total_price: z.string().regex(/^-?\\d{0,8}(?:\\.\\d{0,2})?$/),
  product_name: z.string(),
  product_sku: z.string(),
  created_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type OrderItem = z.infer<typeof OrderItemSchema>
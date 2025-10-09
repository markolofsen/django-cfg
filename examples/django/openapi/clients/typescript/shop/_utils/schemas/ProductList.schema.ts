/**
 * Zod schema for ProductList
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for product list view.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'
import { ShopCategorySchema } from './ShopCategory.schema'

/**
 * Serializer for product list view.
 */
export const ProductListSchema = z.object({
  id: z.number().int(),
  name: z.string().max(200),
  slug: z.string().max(200).regex(/^[-a-zA-Z0-9_]+$/).optional(),
  short_description: z.string().max(500).optional(),
  price: z.string().regex(/^-?\\d{0,8}(?:\\.\\d{0,2})?$/),
  sale_price: z.string().regex(/^-?\\d{0,8}(?:\\.\\d{0,2})?$/).optional(),
  current_price: z.string().regex(/^-?\\d{0,8}(?:\\.\\d{0,2})?$/),
  is_on_sale: z.boolean(),
  discount_percentage: z.number().int(),
  category: ShopCategorySchema,
  image: z.string().url().optional(),
  status: z.nativeEnum(Enums.ProductListStatus).optional(),
  is_featured: z.boolean().optional(),
  is_digital: z.boolean().optional(),
  stock_quantity: z.number().int().min(0.0).max(9.223372036854776e+18).optional(),
  is_in_stock: z.boolean(),
  views_count: z.number().int().min(0.0).max(9.223372036854776e+18).optional(),
  sales_count: z.number().int().min(0.0).max(9.223372036854776e+18).optional(),
  created_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ProductList = z.infer<typeof ProductListSchema>
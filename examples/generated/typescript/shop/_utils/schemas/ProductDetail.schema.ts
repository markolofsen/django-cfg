/**
 * Zod schema for ProductDetail
 *
 * This schema provides runtime validation and type inference.
 *  * Serializer for product detail view.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'
import { ShopCategorySchema } from './ShopCategory.schema'

/**
 * Serializer for product detail view.
 */
export const ProductDetailSchema = z.object({
  id: z.number().int(),
  name: z.string().max(200),
  slug: z.string().max(200).regex(/^[-a-zA-Z0-9_]+$/).optional(),
  description: z.string(),
  short_description: z.string().max(500).optional(),
  price: z.string().regex(/^-?\\d{0,8}(?:\\.\\d{0,2})?$/),
  sale_price: z.string().regex(/^-?\\d{0,8}(?:\\.\\d{0,2})?$/).optional(),
  current_price: z.string().regex(/^-?\\d{0,8}(?:\\.\\d{0,2})?$/),
  is_on_sale: z.boolean(),
  discount_percentage: z.number().int(),
  sku: z.string().max(100),
  stock_quantity: z.number().int().min(0.0).max(9.223372036854776e+18).optional(),
  manage_stock: z.boolean().optional(),
  is_in_stock: z.boolean(),
  category: ShopCategorySchema,
  image: z.string().url().optional(),
  status: z.nativeEnum(Enums.ProductDetailStatus).optional(),
  is_featured: z.boolean().optional(),
  is_digital: z.boolean().optional(),
  meta_title: z.string().max(60).optional(),
  meta_description: z.string().max(160).optional(),
  views_count: z.number().int().min(0.0).max(9.223372036854776e+18).optional(),
  sales_count: z.number().int().min(0.0).max(9.223372036854776e+18).optional(),
  weight: z.string().regex(/^-?\\d{0,6}(?:\\.\\d{0,2})?$/).optional(),
  length: z.string().regex(/^-?\\d{0,6}(?:\\.\\d{0,2})?$/).optional(),
  width: z.string().regex(/^-?\\d{0,6}(?:\\.\\d{0,2})?$/).optional(),
  height: z.string().regex(/^-?\\d{0,6}(?:\\.\\d{0,2})?$/).optional(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ProductDetail = z.infer<typeof ProductDetailSchema>